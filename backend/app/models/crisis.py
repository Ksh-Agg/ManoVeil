import enum
import uuid
from datetime import datetime
from sqlalchemy import String, Float, Boolean, Text, Enum, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class CrisisSeverity(str, enum.Enum):
    YELLOW_FLAG = "yellow_flag"
    ORANGE = "orange"
    RED = "red"
    SOS = "sos"


class CrisisEvent(Base):
    __tablename__ = "crisis_events"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    severity: Mapped[CrisisSeverity] = mapped_column(Enum(CrisisSeverity), nullable=False)
    trigger_source: Mapped[str] = mapped_column(String(50), nullable=False)
    trigger_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    trigger_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    action_taken: Mapped[str] = mapped_column(String(100), nullable=False)
    resolved: Mapped[bool] = mapped_column(Boolean, default=False)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="crisis_events")
