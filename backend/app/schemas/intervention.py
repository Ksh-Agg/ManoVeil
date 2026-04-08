from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field


class InterventionRead(BaseModel):
    id: UUID
    title: str
    description: str
    intervention_type: str
    content: dict
    target_personas: list[str]
    target_categories: list[str] | None
    duration_minutes: int | None
    model_config = {"from_attributes": True}


class CompletionCreate(BaseModel):
    feedback_rating: int | None = Field(None, ge=1, le=5)
    feedback_note: str | None = Field(None, max_length=2000)


class CompletionRead(BaseModel):
    id: UUID
    user_id: UUID
    intervention_id: UUID
    feedback_rating: int | None
    feedback_note: str | None
    completed_at: datetime
    model_config = {"from_attributes": True}
