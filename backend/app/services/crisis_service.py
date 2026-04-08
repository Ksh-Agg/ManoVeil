from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.crisis import CrisisEvent, CrisisSeverity
from app.schemas.crisis import CrisisResource
from app.core.constants import CRISIS_KEYWORDS, CRISIS_HOTLINES


def check_crisis(text: str, score: float | None = None) -> tuple[bool, CrisisSeverity | None]:
    text_lower = text.lower()
    keyword_hit = any(kw in text_lower for kw in CRISIS_KEYWORDS)

    if keyword_hit:
        return True, CrisisSeverity.RED
    if score is not None and score >= 9.0:
        return True, CrisisSeverity.SOS
    return False, None


async def trigger_sos(db: AsyncSession, user_id, source: str = "sos_button", score: float | None = None, text: str | None = None) -> CrisisEvent:
    event = CrisisEvent(
        user_id=user_id,
        severity=CrisisSeverity.SOS,
        trigger_source=source,
        trigger_score=score,
        trigger_text=text[:200] if text else None,
        action_taken="crisis_resources_shown",
    )
    db.add(event)
    await db.flush()
    await db.refresh(event)
    return event


def get_crisis_resources() -> list[CrisisResource]:
    return [CrisisResource(**h) for h in CRISIS_HOTLINES]


async def get_user_crisis_events(db: AsyncSession, user_id, limit=20) -> list[CrisisEvent]:
    result = await db.execute(
        select(CrisisEvent)
        .where(CrisisEvent.user_id == user_id)
        .order_by(desc(CrisisEvent.created_at))
        .limit(limit)
    )
    return list(result.scalars().all())
