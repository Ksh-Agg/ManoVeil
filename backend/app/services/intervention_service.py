from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.intervention import Intervention, InterventionCompletion
from app.models.user import Persona
from app.models.stress_score import ScoreCategory
from app.schemas.intervention import CompletionCreate


async def get_recommended_interventions(
    db: AsyncSession, persona: Persona, category: ScoreCategory | None = None
) -> list[Intervention]:
    stmt = select(Intervention).where(
        Intervention.target_personas.contains([persona.value])
    )
    if category:
        stmt = stmt.where(Intervention.target_categories.contains([category.value]))
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_intervention_by_id(db: AsyncSession, intervention_id) -> Intervention | None:
    result = await db.execute(select(Intervention).where(Intervention.id == intervention_id))
    return result.scalar_one_or_none()


async def complete_intervention(
    db: AsyncSession, user_id, intervention_id, data: CompletionCreate
) -> InterventionCompletion:
    completion = InterventionCompletion(
        user_id=user_id,
        intervention_id=intervention_id,
        feedback_rating=data.feedback_rating,
        feedback_note=data.feedback_note,
    )
    db.add(completion)
    await db.flush()
    await db.refresh(completion)
    return completion


async def get_completion_history(db: AsyncSession, user_id) -> list[InterventionCompletion]:
    result = await db.execute(
        select(InterventionCompletion)
        .where(InterventionCompletion.user_id == user_id)
        .order_by(desc(InterventionCompletion.completed_at))
    )
    return list(result.scalars().all())
