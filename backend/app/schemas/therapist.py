from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field
from app.schemas.user import UserRead
from app.models.stress_score import ScoreCategory


class NoteCreate(BaseModel):
    patient_id: UUID
    content: str = Field(..., min_length=1, max_length=10000)
    note_type: str = "session_note"


class NoteRead(BaseModel):
    id: UUID
    therapist_id: UUID
    patient_id: UUID
    content: str
    note_type: str
    created_at: datetime
    updated_at: datetime
    therapist_name: str | None = None
    model_config = {"from_attributes": True}


class PatientSummary(BaseModel):
    user: UserRead
    latest_score: float | None
    latest_category: ScoreCategory | None
    score_trend: str | None  # "improving", "stable", "declining"
    last_active: datetime | None
    crisis_count: int = 0
    notes_count: int = 0


class PatientTimeline(BaseModel):
    patient: UserRead
    assessments: list[dict]
    stress_scores: list[dict]
    mood_entries: list[dict]
    crisis_events: list[dict]
    notes: list[dict]


class AIGeneratedSummary(BaseModel):
    patient_id: UUID
    summary: str
    key_observations: list[str]
    recommendations: list[str]
    risk_level: str
    generated_at: datetime


class AlertRead(BaseModel):
    patient: UserRead
    alert_type: str  # "score_increase", "crisis_event", "missed_checkin"
    severity: str
    message: str
    created_at: datetime


class LinkPatientRequest(BaseModel):
    patient_id: UUID
    is_primary: bool = False
