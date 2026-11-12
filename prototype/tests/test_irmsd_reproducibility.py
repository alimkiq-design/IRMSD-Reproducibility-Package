from datetime import date
from decimal import Decimal
import uuid

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import (
    Base, Project, User, Requirement, DevelopmentTask, NLPPrediction,
    RiskRecord, MitigationAction
)
from app.irmsd_engine import IRMSDDecisionEngine


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    session = Session()
    project = Project(project_name="Test Project", domain_type="Payments", alpha_cal=Decimal("0.30"))
    user = User(full_name="Test Owner", role="Developer", experience_yrs=5)
    session.add_all([project, user])
    session.flush()
    requirement = Requirement(
        project_id=project.project_id,
        user_story_text="Sync payments",
        acceptance_criteria="Ledger reconciles"
    )
    session.add(requirement)
    session.flush()
    task = DevelopmentTask(
        req_id=requirement.req_id,
        assignee_id=user.user_id,
        e_init=Decimal("10.00"),
        e_adj=Decimal("10.00")
    )
    session.add(task)
    session.flush()
    prediction = NLPPrediction(
        task_id=task.task_id,
        req_id=requirement.req_id,
        candidate_category="R4",
        confidence_score=Decimal("0.920")
    )
    session.add(prediction)
    session.commit()
    yield session, project, user, requirement, task, prediction
    session.close()
    engine.dispose()


def apply(session, user, prediction, p=4, i=5):
    return IRMSDDecisionEngine(session).validate_and_apply_gating(
        pred_id=prediction.pred_id,
        decision="Accepted",
        p_val=p,
        i_val=i,
        owner_id=user.user_id,
        due_date=date(2026, 12, 1)
    )


def test_repeated_registration_is_idempotent_for_same_active_task_category(db_session):
    session, project, user, requirement, task, prediction = db_session
    first = apply(session, user, prediction)
    second = apply(session, user, prediction)
    assert session.query(RiskRecord).filter_by(task_id=task.task_id, category_code="R4").count() == 1
    assert first["risk_id"] == second["risk_id"]
    assert session.query(MitigationAction).count() == 1


def test_distinct_risk_categories_for_same_task_are_not_merged(db_session):
    session, project, user, requirement, task, prediction = db_session
    apply(session, user, prediction)
    second_prediction = NLPPrediction(
        task_id=task.task_id,
        req_id=requirement.req_id,
        candidate_category="R5",
        confidence_score=Decimal("0.890")
    )
    session.add(second_prediction)
    session.commit()
    apply(session, user, second_prediction)
    assert session.query(RiskRecord).filter_by(task_id=task.task_id).count() == 2


def test_effort_calculation_known_example_and_validation():
    assert IRMSDDecisionEngine.calculate_adjusted_effort(
        Decimal("10.00"), 20, Decimal("0.30")
    ) == Decimal("12.40")
    with pytest.raises(ValueError):
        IRMSDDecisionEngine.calculate_adjusted_effort(
            Decimal("10.00"), 26, Decimal("0.30")
        )


def test_high_risk_blocks_task_and_creates_spike(db_session):
    session, project, user, requirement, task, prediction = db_session
    result = apply(session, user, prediction, p=4, i=5)
    session.refresh(task)
    assert result["governing_level"] == "High"
    assert task.workflow_status == "Blocked_Spike"
    assert session.query(MitigationAction).filter_by(action_type="Spike").count() == 1


def test_rejected_candidate_does_not_register_risk(db_session):
    session, project, user, requirement, task, prediction = db_session
    result = IRMSDDecisionEngine(session).validate_and_apply_gating(
        pred_id=prediction.pred_id,
        decision="Rejected",
        p_val=4,
        i_val=5,
        owner_id=user.user_id,
        due_date=date(2026, 12, 1)
    )
    assert result["status"] == "Rejected"
    assert session.query(RiskRecord).count() == 0
    assert prediction.human_decision == "Rejected"


def test_separate_prediction_for_same_active_category_reuses_canonical_risk(db_session):
    session, project, user, requirement, task, prediction = db_session
    first = apply(session, user, prediction)
    duplicate_prediction = NLPPrediction(
        task_id=task.task_id,
        req_id=requirement.req_id,
        candidate_category="R4",
        confidence_score=Decimal("0.910")
    )
    session.add(duplicate_prediction)
    session.commit()
    second = apply(session, user, duplicate_prediction)
    assert second["duplicate"] is True
    assert second["risk_id"] == first["risk_id"]
    assert session.query(RiskRecord).filter_by(task_id=task.task_id, category_code="R4").count() == 1
    assert session.query(MitigationAction).count() == 1


def test_closed_risk_does_not_block_new_lifecycle_instance(db_session):
    session, project, user, requirement, task, prediction = db_session
    first = apply(session, user, prediction)
    original = session.query(RiskRecord).filter_by(
        risk_id=uuid.UUID(first["risk_id"])
    ).one()
    original.risk_status = "Closed"
    second_prediction = NLPPrediction(
        task_id=task.task_id,
        req_id=requirement.req_id,
        candidate_category="R4",
        confidence_score=Decimal("0.930")
    )
    session.add(second_prediction)
    session.commit()
    second = apply(session, user, second_prediction)
    assert second.get("duplicate", False) is False
    assert second["risk_id"] != first["risk_id"]
    assert session.query(RiskRecord).filter_by(task_id=task.task_id, category_code="R4").count() == 2


@pytest.mark.parametrize(
    "p,i,expected_level,expected_action",
    [(1, 2, "Low", 0), (2, 4, "Medium", 1)],
)
def test_low_and_medium_risk_gating(db_session, p, i, expected_level, expected_action):
    session, project, user, requirement, task, prediction = db_session
    result = apply(session, user, prediction, p=p, i=i)
    assert result["governing_level"] == expected_level
    assert session.query(MitigationAction).count() == expected_action
