from datetime import datetime, date, time
from uuid import UUID
from pydantic import BaseModel, Field
from app.models.tracker import MoodLevel


class MoodCreate(BaseModel):
    mood_level: MoodLevel
    emoji: str | None = None
    note: str | None = Field(None, max_length=2000)


class MoodRead(BaseModel):
    id: UUID
    mood_level: MoodLevel
    emoji: str | None
    note: str | None
    sentiment_score: float | None
    recorded_at: datetime
    model_config = {"from_attributes": True}


class SleepCreate(BaseModel):
    sleep_duration: float = Field(..., ge=0, le=24)
    sleep_quality: int = Field(..., ge=1, le=5)
    bedtime: time | None = None
    wake_time: time | None = None
    disturbances: int = Field(0, ge=0)
    note: str | None = Field(None, max_length=2000)


class SleepRead(BaseModel):
    id: UUID
    sleep_duration: float
    sleep_quality: int
    bedtime: time | None
    wake_time: time | None
    disturbances: int
    note: str | None
    recorded_at: datetime
    model_config = {"from_attributes": True}


class ActivityCreate(BaseModel):
    activity_type: str = Field(..., max_length=100)
    duration_minutes: int | None = Field(None, ge=0)
    intensity: int | None = Field(None, ge=1, le=5)
    note: str | None = Field(None, max_length=2000)


class ActivityRead(BaseModel):
    id: UUID
    activity_type: str
    duration_minutes: int | None
    intensity: int | None
    note: str | None
    recorded_at: datetime
    model_config = {"from_attributes": True}


class SocialCreate(BaseModel):
    interactions_count: int = Field(..., ge=0)
    quality_rating: int = Field(..., ge=1, le=5)
    isolation_feeling: int = Field(..., ge=1, le=5)
    note: str | None = Field(None, max_length=2000)
    week_start: date


class SocialRead(BaseModel):
    id: UUID
    interactions_count: int
    quality_rating: int
    isolation_feeling: int
    note: str | None
    week_start: date
    recorded_at: datetime
    model_config = {"from_attributes": True}


class TrackerSummary(BaseModel):
    avg_mood_7d: float | None
    avg_sleep_quality_7d: float | None
    avg_sleep_duration_7d: float | None
    total_activities_7d: int
    avg_social_quality_7d: float | None
    mood_trend: str  # "improving", "stable", "declining"
