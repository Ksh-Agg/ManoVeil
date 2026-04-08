from datetime import datetime, timedelta, timezone
from sqlalchemy import select, desc, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.stress_score import StressScore, ScoreCategory
from app.models.assessment import Assessment
from app.models.chat import ChatMessage
from app.models.tracker import MoodEntry, SleepEntry, MoodLevel
from app.schemas.stress import SHAPExplanation
from app.core.constants import TIER_BOUNDARIES, YELLOW_FLAG_THRESHOLD, FUSION_WEIGHTS
from app.services.assessment_service import categorize_score


MOOD_NUMERIC = {
    MoodLevel.VERY_GOOD: 2.0, MoodLevel.GOOD: 4.0,
    MoodLevel.NEUTRAL: 5.0, MoodLevel.BAD: 7.0, MoodLevel.VERY_BAD: 9.0,
}


def check_yellow_flag(score: float) -> bool:
    return any(abs(score - b) <= YELLOW_FLAG_THRESHOLD for b in TIER_BOUNDARIES)


async def compute_stress_score(db: AsyncSession, user_id) -> StressScore:
    # Get latest assessment normalized score
    result = await db.execute(
        select(Assessment.normalized_score, Assessment.id)
        .where(Assessment.user_id == user_id)
        .order_by(desc(Assessment.completed_at))
        .limit(1)
    )
    row = result.first()
    psychometric = row[0] if row else 5.0
    assessment_id = row[1] if row else None

    # Get avg sentiment from recent chat messages
    week_ago = datetime.now(timezone.utc) - timedelta(days=7)
    result = await db.execute(
        select(func.avg(ChatMessage.sentiment_score))
        .where(ChatMessage.sentiment_score.isnot(None))
        .where(ChatMessage.created_at >= week_ago)
        .join(ChatMessage.session)
        .where(ChatMessage.session.has(user_id=user_id))
    )
    avg_sentiment = result.scalar()
    nlp_score = (1 - avg_sentiment) * 10 if avg_sentiment is not None else 5.0  # invert: negative sentiment = high stress
    nlp_score = max(0, min(10, nlp_score))

    # Get mood trend
    result = await db.execute(
        select(MoodEntry.mood_level)
        .where(MoodEntry.user_id == user_id)
        .order_by(desc(MoodEntry.recorded_at))
        .limit(7)
    )
    moods = result.scalars().all()
    mood_avg = sum(MOOD_NUMERIC.get(m, 5.0) for m in moods) / len(moods) if moods else 5.0

    # Get sleep quality
    result = await db.execute(
        select(func.avg(SleepEntry.sleep_quality))
        .where(SleepEntry.user_id == user_id)
        .where(SleepEntry.recorded_at >= week_ago)
    )
    sleep_avg = result.scalar()
    sleep_stress = (5 - (sleep_avg or 3)) * 2  # poor sleep (1) -> 8, good sleep (5) -> 0

    # Fuse scores
    fused = FUSION_WEIGHTS["psychometric"] * psychometric + FUSION_WEIGHTS["nlp"] * nlp_score
    fused = max(0, min(10, fused))

    category = categorize_score(fused)
    yellow = check_yellow_flag(fused)

    # Generate feature-based SHAP-like explanation
    features = {
        "assessment_score": round(psychometric, 2),
        "chat_sentiment": round(nlp_score, 2),
        "mood_trend": round(mood_avg, 2),
        "sleep_quality": round(sleep_stress, 2),
    }
    base = 5.0
    shap_vals = {
        "assessment_score": round((psychometric - base) * 0.6, 2),
        "chat_sentiment": round((nlp_score - base) * 0.4, 2),
        "mood_trend": round((mood_avg - base) * 0.15, 2),
        "sleep_quality": round(sleep_stress * 0.1, 2),
    }

    score = StressScore(
        user_id=user_id,
        psychometric_score=psychometric,
        nlp_score=nlp_score,
        fused_score=fused,
        category=category,
        yellow_flag=yellow,
        source_assessment_id=assessment_id,
        shap_values=shap_vals,
        feature_values=features,
        model_version="v1.0-fusion",
    )
    db.add(score)
    await db.flush()
    await db.refresh(score)
    return score


async def get_latest_score(db: AsyncSession, user_id) -> StressScore | None:
    result = await db.execute(
        select(StressScore)
        .where(StressScore.user_id == user_id)
        .order_by(desc(StressScore.computed_at))
        .limit(1)
    )
    return result.scalar_one_or_none()


async def get_stress_history(db: AsyncSession, user_id, days: int = 30) -> list[StressScore]:
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    result = await db.execute(
        select(StressScore)
        .where(StressScore.user_id == user_id)
        .where(StressScore.computed_at >= cutoff)
        .order_by(desc(StressScore.computed_at))
    )
    return list(result.scalars().all())


async def get_shap_explanation(db: AsyncSession, score_id) -> SHAPExplanation | None:
    result = await db.execute(select(StressScore).where(StressScore.id == score_id))
    score = result.scalar_one_or_none()
    if not score or not score.shap_values:
        return None

    names = list(score.shap_values.keys())
    vals = list(score.shap_values.values())
    feat_vals = [score.feature_values.get(n, 0) for n in names] if score.feature_values else [0] * len(names)

    return SHAPExplanation(
        score_id=score.id,
        fused_score=score.fused_score,
        category=score.category,
        feature_names=names,
        feature_values=feat_vals,
        shap_values=vals,
        base_value=5.0,
    )
