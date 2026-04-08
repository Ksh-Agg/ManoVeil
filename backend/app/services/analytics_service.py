from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User, AgeGroup
from app.models.assessment import Assessment
from app.models.stress_score import StressScore, ScoreCategory


async def get_platform_stats(db: AsyncSession) -> dict:
    total_users = (await db.execute(select(func.count(User.id)))).scalar() or 0
    active_users = (await db.execute(
        select(func.count(User.id)).where(User.is_active == True)
    )).scalar() or 0
    total_assessments = (await db.execute(select(func.count(Assessment.id)))).scalar() or 0
    total_scores = (await db.execute(select(func.count(StressScore.id)))).scalar() or 0

    # Avg score by age group
    age_stats = {}
    for ag in AgeGroup:
        result = await db.execute(
            select(func.avg(StressScore.fused_score))
            .join(User, StressScore.user_id == User.id)
            .where(User.age_group == ag)
        )
        avg = result.scalar()
        age_stats[ag.value] = round(avg, 2) if avg else None

    # Category distribution
    cat_dist = {}
    for cat in ScoreCategory:
        result = await db.execute(
            select(func.count(StressScore.id))
            .where(StressScore.category == cat)
        )
        cat_dist[cat.value] = result.scalar() or 0

    return {
        "total_users": total_users,
        "active_users": active_users,
        "total_assessments": total_assessments,
        "total_stress_scores": total_scores,
        "avg_score_by_age_group": age_stats,
        "category_distribution": cat_dist,
    }
