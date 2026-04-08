from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field
from app.models.user import Persona


class ChatSessionCreate(BaseModel):
    pass  # persona is auto-assigned from user


class ChatSessionRead(BaseModel):
    id: UUID
    user_id: UUID
    persona: Persona
    started_at: datetime
    ended_at: datetime | None
    summary: str | None
    message_count: int = 0
    model_config = {"from_attributes": True}


class MessageCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=5000)


class MessageRead(BaseModel):
    id: UUID
    session_id: UUID
    role: str
    content: str
    sentiment_score: float | None
    crisis_flag: bool
    created_at: datetime
    model_config = {"from_attributes": True}


class ChatResponse(BaseModel):
    user_message: MessageRead
    bot_message: MessageRead
    crisis_detected: bool = False
    crisis_resources: list[dict] | None = None
