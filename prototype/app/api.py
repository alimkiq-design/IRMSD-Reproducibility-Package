import os
import uuid
from datetime import date

from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.irmsd_engine import IRMSDDecisionEngine

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:postgres@localhost:5432/irmsd_db"
)
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app = FastAPI(title="IRMSD Prototype Backend API", version="0.1.0")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class RiskValidationRequest(BaseModel):
    pred_id: uuid.UUID
    decision: str = Field(..., pattern="^(Accepted|Rejected|Modified)$")
    p_val: int = Field(..., ge=1, le=5)
    i_val: int = Field(..., ge=1, le=5)
    owner_id: uuid.UUID
    due_date: date


@app.post("/api/v1/risks/validate")
def validate_candidate_risk(
    payload: RiskValidationRequest,
    db: Session = Depends(get_db)
):
    decision_engine = IRMSDDecisionEngine(db)
    try:
        return decision_engine.validate_and_apply_gating(
            pred_id=payload.pred_id,
            decision=payload.decision,
            p_val=payload.p_val,
            i_val=payload.i_val,
            owner_id=payload.owner_id,
            due_date=payload.due_date
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
