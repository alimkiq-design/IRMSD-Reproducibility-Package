import uuid
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import (
    Column, String, Integer, Numeric, Text, Date, DateTime, ForeignKey,
    Computed, Index
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Project(Base):
    __tablename__ = "project"
    project_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_name = Column(String(150), unique=True, nullable=False)
    domain_type = Column(String(50), nullable=False)
    alpha_cal = Column(Numeric(3, 2), nullable=False, default=Decimal("0.30"))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class User(Base):
    __tablename__ = "user"
    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name = Column(String(100), nullable=False)
    role = Column(String(30), nullable=False)
    experience_yrs = Column(Integer, nullable=False)


class Requirement(Base):
    __tablename__ = "requirement"
    req_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("project.project_id"), nullable=False)
    user_story_text = Column(Text, nullable=False)
    acceptance_criteria = Column(Text, nullable=False)
    priority_level = Column(String(20), nullable=False, default="Medium")


class DevelopmentTask(Base):
    __tablename__ = "development_task"
    task_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    req_id = Column(UUID(as_uuid=True), ForeignKey("requirement.req_id"), nullable=False)
    assignee_id = Column(UUID(as_uuid=True), ForeignKey("user.user_id"), nullable=True)
    e_init = Column(Numeric(6, 2), nullable=False)
    e_adj = Column(Numeric(6, 2), nullable=False)
    governing_risk_level = Column(String(10), nullable=False, default="Low")
    workflow_status = Column(String(20), nullable=False, default="Backlog")


class NLPPrediction(Base):
    __tablename__ = "nlp_prediction"
    pred_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id = Column(UUID(as_uuid=True), ForeignKey("development_task.task_id"), nullable=False)
    req_id = Column(UUID(as_uuid=True), ForeignKey("requirement.req_id"), nullable=False)
    model_version = Column(String(50), nullable=False, default="bert-base-uncased-v1")
    candidate_category = Column(String(5), nullable=False)
    confidence_score = Column(Numeric(4, 3), nullable=False)
    extracted_text_span = Column(Text, nullable=True)
    human_decision = Column(String(15), nullable=False, default="Pending")
    reviewed_at = Column(DateTime(timezone=True), nullable=True)


class RiskRecord(Base):
    __tablename__ = "risk_record"
    risk_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id = Column(UUID(as_uuid=True), ForeignKey("development_task.task_id"), nullable=False)
    pred_id = Column(UUID(as_uuid=True), ForeignKey("nlp_prediction.pred_id"), unique=True, nullable=True)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("user.user_id"), nullable=False)
    category_code = Column(String(5), nullable=False)
    p_init = Column(Integer, nullable=False)
    i_init = Column(Integer, nullable=False)
    r_init = Column(Integer, Computed("p_init * i_init", persisted=True))
    p_curr = Column(Integer, nullable=False)
    i_curr = Column(Integer, nullable=False)
    r_curr = Column(Integer, Computed("p_curr * i_curr", persisted=True))
    severity_tier = Column(String(10), Computed(
        "CASE WHEN (p_curr * i_curr) <= 6 THEN 'Low' "
        "WHEN (p_curr * i_curr) <= 14 THEN 'Medium' ELSE 'High' END",
        persisted=True
    ))
    risk_status = Column(String(15), nullable=False, default="Open")
    identified_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class MitigationAction(Base):
    __tablename__ = "mitigation_action"
    mitigation_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    risk_id = Column(UUID(as_uuid=True), ForeignKey("risk_record.risk_id"), nullable=False)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("user.user_id"), nullable=False)
    action_type = Column(String(25), nullable=False)
    buffer_hours = Column(Numeric(5, 2), nullable=False, default=Decimal("0.00"))
    due_date = Column(Date, nullable=False)
    action_status = Column(String(15), nullable=False, default="Planned")
    started_at = Column(DateTime(timezone=True), nullable=True)


class Verification(Base):
    __tablename__ = "verification"
    verif_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mitigation_id = Column(UUID(as_uuid=True), ForeignKey("mitigation_action.mitigation_id"), nullable=False)
    evidence_type = Column(String(30), nullable=False)
    artifact_link = Column(String(255), nullable=False)
    verified_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


# Database-level protection against concurrent duplicate active registrations.
# PostgreSQL/SQLite partial unique index; SQLite behavior was exercised by tests.
Index(
    "uq_active_risk_task_category",
    RiskRecord.task_id,
    RiskRecord.category_code,
    unique=True,
    postgresql_where=RiskRecord.risk_status.in_(("Open", "Mitigating")),
    sqlite_where=RiskRecord.risk_status.in_(("Open", "Mitigating")),
)
