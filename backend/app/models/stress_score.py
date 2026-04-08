import enum
import uuid
from datetime import datetime
from sqlalchemy import String, Float, Boolean, Enum, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class ScoreCategory(str, enum.Enum):
    MINIMAL = "minimal"
    MILD = "mild"
    MODERATE = "moderate"
    MODERATELY_SEVERE = "moderately_severe"
    SEVERE = "severe"


class StressScore(Base):
    __tablename__ = "stress_scores"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    psychometric_score: Mapped[float] = mapped_column(Float, nullable=False)
    nlp_score: Mapped[float] = mapped_column(Float, nullable=False)
    fused_score: Mapped[float] = mapped_column(Float, nullable=False)
    category: Mapped[ScoreCategory] = mapped_column(Enum(ScoreCategory), nullable=False)
    yellow_flag: Mapped[bool] = mapped_column(Boolean, default=False)
    source_assessment_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("assessments.id"), nullable=True
    )
    source_chat_session_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("chat_sessions.id"), nullable=True
    )
    shap_values: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    feature_values: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    model_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    computed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="stress_scores")
