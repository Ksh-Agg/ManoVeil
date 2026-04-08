from datetime import datetime
from uuid import UUID
from pydantic import BaseModel
from app.models.assessment import AssessmentType
from app.models.stress_score import ScoreCategory


class AssessmentCreate(BaseModel):
    assessment_type: AssessmentType
    raw_responses: dict  # {question_id: answer_value}


class AssessmentRead(BaseModel):
    id: UUID
    user_id: UUID
    assessment_type: AssessmentType
    raw_responses: dict
    total_score: float
    subscale_scores: dict | None
    normalized_score: float
    category: ScoreCategory
    completed_at: datetime
    created_at: datetime

    model_config = {"from_attributes": True}


class InstrumentQuestion(BaseModel):
    id: str
    text: str
    options: list[dict]
    subscale: str | None = None


class InstrumentInfo(BaseModel):
    type: AssessmentType
    name: str
    description: str
    question_count: int
    estimated_minutes: int
    questions: list[InstrumentQuestion] | None = None
