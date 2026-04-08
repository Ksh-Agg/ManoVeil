from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, desc, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.permissions import get_current_user
from app.models.user import User
from app.models.tracker import MoodEntry, SleepEntry, ActivityEntry, SocialEntry, MoodLevel
from app.schemas.tracker import (
    MoodCreate, MoodRead, SleepCreate, SleepRead,
    ActivityCreate, ActivityRead, SocialCreate, SocialRead, TrackerSummary,
)
from app.services.chat_service import analyze_sentiment

router = APIRouter()

MOOD_NUMERIC = {MoodLevel.VERY_GOOD: 1, MoodLevel.GOOD: 2, MoodLevel.NEUTRAL: 3, MoodLevel.BAD: 4, MoodLevel.VERY_BAD: 5}


# ─── Mood ───
@router.post("/mood", response_model=MoodRead, status_code=201)
async def create_mood(data: MoodCreate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    sentiment = analyze_sentiment(data.note) if data.note else None
    entry = MoodEntry(user_id=user.id, mood_level=data.mood_level, emoji=data.emoji, note=data.note, sentiment_score=sentiment)
    db.add(entry)
    await db.flush()
    await db.refresh(entry)
    return MoodRead.model_validate(entry)


@router.get("/mood", response_model=list[MoodRead])
async def list_mood(limit: int = Query(20, ge=1, le=100), offset: int = Query(0, ge=0),
                    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(MoodEntry).where(MoodEntry.user_id == user.id).order_by(desc(MoodEntry.recorded_at)).limit(limit).offset(offset))
    return [MoodRead.model_validate(e) for e in result.scalars().all()]


# ─── Sleep ───
@router.post("/sleep", response_model=SleepRead, status_code=201)
async def create_sleep(data: SleepCreate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    entry = SleepEntry(user_id=user.id, sleep_duration=data.sleep_duration, sleep_quality=data.sleep_quality,
                       bedtime=data.bedtime, wake_time=data.wake_time, disturbances=data.disturbances, note=data.note)
    db.add(entry)
    await db.flush()
    await db.refresh(entry)
    return SleepRead.model_validate(entry)


@router.get("/sleep", response_model=list[SleepRead])
async def list_sleep(limit: int = Query(20, ge=1, le=100), offset: int = Query(0, ge=0),
                     user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SleepEntry).where(SleepEntry.user_id == user.id).order_by(desc(SleepEntry.recorded_at)).limit(limit).offset(offset))
    return [SleepRead.model_validate(e) for e in result.scalars().all()]


# ─── Activity ───
@router.post("/activity", response_model=ActivityRead, status_code=201)
async def create_activity(data: ActivityCreate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    entry = ActivityEntry(user_id=user.id, activity_type=data.activity_type, duration_minutes=data.duration_minutes,
                          intensity=data.intensity, note=data.note)
    db.add(entry)
    await db.flush()
    await db.refresh(entry)
    return ActivityRead.model_validate(entry)


@router.get("/activity", response_model=list[ActivityRead])
async def list_activity(limit: int = Query(20, ge=1, le=100), offset: int = Query(0, ge=0),
                        user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ActivityEntry).where(ActivityEntry.user_id == user.id).order_by(desc(ActivityEntry.recorded_at)).limit(limit).offset(offset))
    return [ActivityRead.model_validate(e) for e in result.scalars().all()]


# ─── Social ───
@router.post("/social", response_model=SocialRead, status_code=201)
async def create_social(data: SocialCreate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    entry = SocialEntry(user_id=user.id, interactions_count=data.interactions_count, quality_rating=data.quality_rating,
                        isolation_feeling=data.isolation_feeling, note=data.note, week_start=data.week_start)
    db.add(entry)
    await db.flush()
    await db.refresh(entry)
    return SocialRead.model_validate(entry)


@router.get("/social", response_model=list[SocialRead])
async def list_social(limit: int = Query(20, ge=1, le=100), offset: int = Query(0, ge=0),
                      user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SocialEntry).where(SocialEntry.user_id == user.id).order_by(desc(SocialEntry.recorded_at)).limit(limit).offset(offset))
    return [SocialRead.model_validate(e) for e in result.scalars().all()]


# ─── Summary ───
@router.get("/summary", response_model=TrackerSummary)
async def tracker_summary(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    week_ago = datetime.now(timezone.utc) - timedelta(days=7)

    mood_result = await db.execute(select(MoodEntry.mood_level).where(MoodEntry.user_id == user.id, MoodEntry.recorded_at >= week_ago))
    moods = mood_result.scalars().all()
    avg_mood = sum(MOOD_NUMERIC.get(m, 3) for m in moods) / len(moods) if moods else None

    sleep_q = await db.execute(select(func.avg(SleepEntry.sleep_quality)).where(SleepEntry.user_id == user.id, SleepEntry.recorded_at >= week_ago))
    sleep_d = await db.execute(select(func.avg(SleepEntry.sleep_duration)).where(SleepEntry.user_id == user.id, SleepEntry.recorded_at >= week_ago))

    activity_count = await db.execute(select(func.count(ActivityEntry.id)).where(ActivityEntry.user_id == user.id, ActivityEntry.recorded_at >= week_ago))

    social_q = await db.execute(select(func.avg(SocialEntry.quality_rating)).where(SocialEntry.user_id == user.id, SocialEntry.recorded_at >= week_ago))

    # Determine trend
    if moods and len(moods) >= 3:
        recent = [MOOD_NUMERIC.get(m, 3) for m in moods[:3]]
        older = [MOOD_NUMERIC.get(m, 3) for m in moods[3:]] if len(moods) > 3 else recent
        trend = "improving" if sum(recent)/len(recent) < sum(older)/len(older) else "declining" if sum(recent)/len(recent) > sum(older)/len(older) else "stable"
    else:
        trend = "stable"

    return TrackerSummary(
        avg_mood_7d=round(avg_mood, 2) if avg_mood else None,
        avg_sleep_quality_7d=round(sleep_q.scalar() or 0, 2) if sleep_q.scalar() else None,
        avg_sleep_duration_7d=round(sleep_d.scalar() or 0, 2) if sleep_d.scalar() else None,
        total_activities_7d=activity_count.scalar() or 0,
        avg_social_quality_7d=round(social_q.scalar() or 0, 2) if social_q.scalar() else None,
        mood_trend=trend,
    )
