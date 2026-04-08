import enum
import uuid
from datetime import datetime, date
from sqlalchemy import String, Boolean, Date, Enum, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class AgeGroup(str, enum.Enum):
    CHILDREN_5_12 = "children_5_12"
    TEENAGERS_13_17 = "teenagers_13_17"
    COLLEGE_18_24 = "college_18_24"
    ADULTS_25_59 = "adults_25_59"
    ELDERLY_60_PLUS = "elderly_60_plus"


class UserRole(str, enum.Enum):
    USER = "user"
    PATIENT = "patient"
    THERAPIST = "therapist"
    ADMIN = "admin"


class Persona(str, enum.Enum):
    MANOMITRA = "manomitra"
    MANOSPARK = "manospark"
    MANOVEIL_CORE = "manoveil_core"
    MANOBALANCE = "manobalance"
    MANOSAATHI = "manosaathi"
    MANOCONNECT = "manoconnect"


AGE_TO_PERSONA = {
    AgeGroup.CHILDREN_5_12: Persona.MANOMITRA,
    AgeGroup.TEENAGERS_13_17: Persona.MANOSPARK,
    AgeGroup.COLLEGE_18_24: Persona.MANOVEIL_CORE,
    AgeGroup.ADULTS_25_59: Persona.MANOBALANCE,
    AgeGroup.ELDERLY_60_PLUS: Persona.MANOSAATHI,
}


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    date_of_birth: Mapped[date] = mapped_column(Date, nullable=False)
    age_group: Mapped[AgeGroup] = mapped_column(Enum(AgeGroup), nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), nullable=False, default=UserRole.USER)
    persona: Mapped[Persona] = mapped_column(Enum(Persona), nullable=False)
    emergency_contact_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    emergency_contact_phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    assessments = relationship("Assessment", back_populates="user", cascade="all, delete-orphan")
    mood_entries = relationship("MoodEntry", back_populates="user", cascade="all, delete-orphan")
    sleep_entries = relationship("SleepEntry", back_populates="user", cascade="all, delete-orphan")
    activity_entries = relationship("ActivityEntry", back_populates="user", cascade="all, delete-orphan")
    social_entries = relationship("SocialEntry", back_populates="user", cascade="all, delete-orphan")
    chat_sessions = relationship("ChatSession", back_populates="user", cascade="all, delete-orphan")
    stress_scores = relationship("StressScore", back_populates="user", cascade="all, delete-orphan")
    crisis_events = relationship("CrisisEvent", back_populates="user", cascade="all, delete-orphan")
