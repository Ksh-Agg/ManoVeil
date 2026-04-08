import json
import os
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.models.assessment import Assessment, AssessmentType
from app.models.user import AgeGroup
from app.models.stress_score import ScoreCategory
from app.schemas.assessment import AssessmentCreate, InstrumentInfo, InstrumentQuestion
from app.core.constants import ASSESSMENT_ELIGIBILITY, ASSESSMENT_MAX_SCORES, SCORE_TIERS

INSTRUMENTS_DIR = Path(__file__).parent.parent / "core" / "instruments"


def categorize_score(normalized: float) -> ScoreCategory:
    if normalized <= 2.0:
        return ScoreCategory.MINIMAL
    elif normalized <= 4.5:
        return ScoreCategory.MILD
    elif normalized <= 7.0:
        return ScoreCategory.MODERATE
    elif normalized <= 8.9:
        return ScoreCategory.MODERATELY_SEVERE
    else:
        return ScoreCategory.SEVERE


def _load_instrument(assessment_type: AssessmentType) -> dict:
    path = INSTRUMENTS_DIR / f"{assessment_type.value}.json"
    if not path.exists():
        return {"name": assessment_type.value.upper().replace("_", "-"), "description": "", "questions": []}
    with open(path) as f:
        return json.load(f)


def get_eligible_instruments(age_group: AgeGroup) -> list[InstrumentInfo]:
    eligible = ASSESSMENT_ELIGIBILITY.get(age_group, [])
    instruments = []
    for at in eligible:
        data = _load_instrument(at)
        instruments.append(InstrumentInfo(
            type=at,
            name=data.get("name", at.value),
            description=data.get("description", ""),
            question_count=len(data.get("questions", [])),
            estimated_minutes=data.get("estimated_minutes", 5),
        ))
    return instruments


def get_instrument_questions(assessment_type: AssessmentType) -> InstrumentInfo:
    data = _load_instrument(assessment_type)
    questions = [
        InstrumentQuestion(
            id=q["id"], text=q["text"],
            options=q.get("options", []),
            subscale=q.get("subscale"),
        )
        for q in data.get("questions", [])
    ]
    return InstrumentInfo(
        type=assessment_type,
        name=data.get("name", assessment_type.value),
        description=data.get("description", ""),
        question_count=len(questions),
        estimated_minutes=data.get("estimated_minutes", 5),
        questions=questions,
    )


def score_assessment(assessment_type: AssessmentType, raw_responses: dict) -> tuple[float, dict | None, float, ScoreCategory]:
    values = [float(v) for v in raw_responses.values()]
    total = sum(values)
    max_score = ASSESSMENT_MAX_SCORES.get(assessment_type, 1.0)
    normalized = min((total / max_score) * 10.0, 10.0)

    subscale_scores = None
    if assessment_type == AssessmentType.DASS_21:
        data = _load_instrument(assessment_type)
        subscales = {"depression": [], "anxiety": [], "stress": []}
        for q in data.get("questions", []):
            sub = q.get("subscale", "stress")
            val = float(raw_responses.get(q["id"], 0))
            if sub in subscales:
                subscales[sub].append(val)
        subscale_scores = {k: sum(v) * 2 for k, v in subscales.items()}

    category = categorize_score(normalized)
    return total, subscale_scores, normalized, category


async def create_assessment(db: AsyncSession, user_id, data: AssessmentCreate) -> Assessment:
    total, subscales, normalized, category = score_assessment(data.assessment_type, data.raw_responses)
    assessment = Assessment(
        user_id=user_id,
        assessment_type=data.assessment_type,
        raw_responses=data.raw_responses,
        total_score=total,
        subscale_scores=subscales,
        normalized_score=normalized,
        category=category,
    )
    db.add(assessment)
    await db.flush()
    await db.refresh(assessment)
    return assessment


async def get_user_assessments(db: AsyncSession, user_id, limit=20, offset=0) -> list[Assessment]:
    result = await db.execute(
        select(Assessment)
        .where(Assessment.user_id == user_id)
        .order_by(desc(Assessment.completed_at))
        .limit(limit).offset(offset)
    )
    return list(result.scalars().all())


async def get_assessment_by_id(db: AsyncSession, assessment_id) -> Assessment | None:
    result = await db.execute(select(Assessment).where(Assessment.id == assessment_id))
    return result.scalar_one_or_none()
