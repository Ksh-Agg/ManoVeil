import enum
import uuid
from datetime import datetime
from sqlalchemy import String, Float, Enum, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from app.models.stress_score import ScoreCategory


class AssessmentType(str, enum.Enum):
    DASS_21 = "dass_21"
    GAD_7 = "gad_7"
    PHQ_9 = "phq_9"
    CDI_2 = "cdi_2"
    SCARED = "scared"
    GDS_15 = "gds_15"


class Assessment(Base):
    __tablename__ = "assessments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    assessment_type: Mapped[AssessmentType] = mapped_column(Enum(AssessmentType), nullable=False)
    raw_responses: Mapped[dict] = mapped_column(JSONB, nullable=False)
    total_score: Mapped[float] = mapped_column(Float, nullable=False)
    subscale_scores: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    normalized_score: Mapped[float] = mapped_column(Float, nullable=False)
    category: Mapped[ScoreCategory] = mapped_column(Enum(ScoreCategory), nullable=False)
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="assessments")
