from datetime import datetime
from uuid import UUID
from pydantic import BaseModel
from app.models.crisis import CrisisSeverity


class CrisisEventCreate(BaseModel):
    trigger_source: str = "sos_button"


class CrisisEventRead(BaseModel):
    id: UUID
    user_id: UUID
    severity: CrisisSeverity
    trigger_source: str
    trigger_score: float | None
    action_taken: str
    resolved: bool
    created_at: datetime
    model_config = {"from_attributes": True}


class CrisisResource(BaseModel):
    name: str
    number: str
    description: str
    hours: str
