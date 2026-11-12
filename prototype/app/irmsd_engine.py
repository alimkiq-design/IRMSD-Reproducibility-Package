import uuid
from datetime import date, datetime, timezone
from decimal import Decimal

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models import (
    Project, Requirement, DevelopmentTask, NLPPrediction, RiskRecord, MitigationAction
)


class IRMSDDecisionEngine:
    def __init__(self, db_session: Session):
        self.db = db_session

    @staticmethod
    def calculate_adjusted_effort(e_init: Decimal, r_max: int, alpha_cal: Decimal) -> Decimal:
        if r_max < 1 or r_max > 25:
            raise ValueError("Risk score r_max must be between 1 and 25.")
        if alpha_cal <= Decimal("0.00") or alpha_cal > Decimal("0.50"):
            raise ValueError("Calibration factor alpha_cal must be in (0.00, 0.50].")
        multiplier = Decimal("1.0") + (alpha_cal * (Decimal(r_max) / Decimal("25.0")))
        return (e_init * multiplier).quantize(Decimal("0.01"))

    def validate_and_apply_gating(
        self,
        pred_id: uuid.UUID,
        decision: str,
        p_val: int,
        i_val: int,
        owner_id: uuid.UUID,
        due_date: date
    ) -> dict:
        pred = self.db.query(NLPPrediction).filter_by(pred_id=pred_id).first()
        if not pred:
            raise ValueError("NLP Prediction record not found.")

        pred.human_decision = decision
        pred.reviewed_at = datetime.now(timezone.utc)

        if decision == "Rejected":
            self.db.commit()
            return {"status": "Rejected", "message": "Candidate risk dismissed by reviewer."}

        # An active risk is unique per task and category. Closed/Verified
        # records remain historical and do not block a later lifecycle.
        existing_risk = (
            self.db.query(RiskRecord)
            .filter(
                RiskRecord.task_id == pred.task_id,
                RiskRecord.category_code == pred.candidate_category,
                RiskRecord.risk_status.in_(("Open", "Mitigating")),
            )
            .order_by(RiskRecord.identified_at.asc())
            .first()
        )
        if existing_risk is not None:
            task = self.db.query(DevelopmentTask).filter_by(task_id=pred.task_id).first()
            self.db.commit()
            return {
                "risk_id": str(existing_risk.risk_id),
                "r_score": existing_risk.r_curr if existing_risk.r_curr is not None else existing_risk.p_curr * existing_risk.i_curr,
                "governing_level": task.governing_risk_level,
                "workflow_status": task.workflow_status,
                "e_adj": float(task.e_adj),
                "mitigation_required": "Existing",
                "duplicate": True,
            }

        risk = RiskRecord(
            task_id=pred.task_id,
            pred_id=pred.pred_id,
            owner_id=owner_id,
            category_code=pred.candidate_category,
            p_init=p_val,
            i_init=i_val,
            p_curr=p_val,
            i_curr=i_val,
            risk_status="Open"
        )
        self.db.add(risk)
        try:
            self.db.flush()
        except IntegrityError:
            # A concurrent request may have passed the pre-check before another
            # transaction inserted the same active task/category risk.
            self.db.rollback()
            pred = self.db.query(NLPPrediction).filter_by(pred_id=pred_id).first()
            if pred is None:
                raise
            pred.human_decision = decision
            pred.reviewed_at = datetime.now(timezone.utc)
            existing_risk = (
                self.db.query(RiskRecord)
                .filter(
                    RiskRecord.task_id == pred.task_id,
                    RiskRecord.category_code == pred.candidate_category,
                    RiskRecord.risk_status.in_(("Open", "Mitigating")),
                )
                .order_by(RiskRecord.identified_at.asc())
                .first()
            )
            if existing_risk is None:
                raise
            task = self.db.query(DevelopmentTask).filter_by(task_id=pred.task_id).first()
            self.db.commit()
            return {
                "risk_id": str(existing_risk.risk_id),
                "r_score": existing_risk.r_curr if existing_risk.r_curr is not None else existing_risk.p_curr * existing_risk.i_curr,
                "governing_level": task.governing_risk_level,
                "workflow_status": task.workflow_status,
                "e_adj": float(task.e_adj),
                "mitigation_required": "Existing",
                "duplicate": True,
            }

        task = self.db.query(DevelopmentTask).filter_by(task_id=pred.task_id).first()
        req = self.db.query(Requirement).filter_by(req_id=task.req_id).first()
        project = self.db.query(Project).filter_by(project_id=req.project_id).first()

        all_task_risks = self.db.query(RiskRecord).filter_by(task_id=task.task_id).all()
        r_max = max(
            r.r_curr if r.r_curr is not None else (r.p_curr * r.i_curr)
            for r in all_task_risks
        )

        task.e_adj = self.calculate_adjusted_effort(task.e_init, r_max, project.alpha_cal)
        buffer_diff = task.e_adj - task.e_init

        if r_max <= 6:
            task.governing_risk_level = "Low"
            action_created = None
        elif r_max <= 14:
            task.governing_risk_level = "Medium"
            action_created = MitigationAction(
                risk_id=risk.risk_id,
                owner_id=owner_id,
                action_type="Peer_Review",
                buffer_hours=buffer_diff,
                due_date=due_date
            )
            self.db.add(action_created)
        else:
            task.governing_risk_level = "High"
            task.workflow_status = "Blocked_Spike"
            action_created = MitigationAction(
                risk_id=risk.risk_id,
                owner_id=owner_id,
                action_type="Spike",
                buffer_hours=buffer_diff,
                due_date=due_date
            )
            self.db.add(action_created)

        self.db.commit()
        return {
            "risk_id": str(risk.risk_id),
            "r_score": r_max,
            "governing_level": task.governing_risk_level,
            "workflow_status": task.workflow_status,
            "e_adj": float(task.e_adj),
            "mitigation_required": action_created.action_type if action_created else "None"
        }
