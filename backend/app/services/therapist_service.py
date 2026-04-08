from datetime import datetime, timedelta, timezone
from sqlalchemy import select, desc, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.models.therapist import PatientTherapistLink, TherapistNote
from app.models.assessment import Assessment
from app.models.stress_score import StressScore
from app.models.tracker import MoodEntry
from app.models.crisis import CrisisEvent
from app.schemas.therapist import (
    PatientSummary, PatientTimeline, AIGeneratedSummary,
    NoteCreate, NoteRead, AlertRead, LinkPatientRequest,
)
from app.schemas.user import UserRead
from app.core.constants import PERSONA_NAMES


async def link_patient(db: AsyncSession, therapist_id, patient_id, is_primary=False):
    link = PatientTherapistLink(
        patient_id=patient_id, therapist_id=therapist_id, is_primary=is_primary
    )
    db.add(link)
    await db.flush()
    await db.refresh(link)
    return link


async def get_linked_patients(db: AsyncSession, therapist_id) -> list[PatientSummary]:
    result = await db.execute(
        select(PatientTherapistLink)
        .where(PatientTherapistLink.therapist_id == therapist_id)
        .where(PatientTherapistLink.unlinked_at.is_(None))
    )
    links = result.scalars().all()

    summaries = []
    for link in links:
        patient_result = await db.execute(select(User).where(User.id == link.patient_id))
        patient = patient_result.scalar_one_or_none()
        if not patient:
            continue

        # Latest score
        score_result = await db.execute(
            select(StressScore)
            .where(StressScore.user_id == patient.id)
            .order_by(desc(StressScore.computed_at)).limit(1)
        )
        latest = score_result.scalar_one_or_none()

        # Crisis count
        crisis_result = await db.execute(
            select(func.count(CrisisEvent.id))
            .where(CrisisEvent.user_id == patient.id)
        )
        crisis_count = crisis_result.scalar() or 0

        # Notes count
        notes_result = await db.execute(
            select(func.count(TherapistNote.id))
            .where(TherapistNote.patient_id == patient.id)
        )
        notes_count = notes_result.scalar() or 0

        summaries.append(PatientSummary(
            user=UserRead.model_validate(patient),
            latest_score=latest.fused_score if latest else None,
            latest_category=latest.category if latest else None,
            score_trend=None,
            last_active=latest.computed_at if latest else None,
            crisis_count=crisis_count,
            notes_count=notes_count,
        ))
    return summaries


async def get_patient_timeline(db: AsyncSession, patient_id) -> dict:
    patient_result = await db.execute(select(User).where(User.id == patient_id))
    patient = patient_result.scalar_one_or_none()

    assessments = await db.execute(
        select(Assessment).where(Assessment.user_id == patient_id).order_by(desc(Assessment.completed_at)).limit(20)
    )
    scores = await db.execute(
        select(StressScore).where(StressScore.user_id == patient_id).order_by(desc(StressScore.computed_at)).limit(30)
    )
    moods = await db.execute(
        select(MoodEntry).where(MoodEntry.user_id == patient_id).order_by(desc(MoodEntry.recorded_at)).limit(30)
    )
    crises = await db.execute(
        select(CrisisEvent).where(CrisisEvent.user_id == patient_id).order_by(desc(CrisisEvent.created_at)).limit(10)
    )
    notes = await db.execute(
        select(TherapistNote).where(TherapistNote.patient_id == patient_id).order_by(desc(TherapistNote.created_at)).limit(20)
    )

    return {
        "patient": UserRead.model_validate(patient) if patient else None,
        "assessments": [{"id": str(a.id), "type": a.assessment_type.value, "score": a.normalized_score, "category": a.category.value, "date": a.completed_at.isoformat()} for a in assessments.scalars().all()],
        "stress_scores": [{"id": str(s.id), "score": s.fused_score, "category": s.category.value, "date": s.computed_at.isoformat()} for s in scores.scalars().all()],
        "mood_entries": [{"id": str(m.id), "mood": m.mood_level.value, "date": m.recorded_at.isoformat()} for m in moods.scalars().all()],
        "crisis_events": [{"id": str(c.id), "severity": c.severity.value, "source": c.trigger_source, "date": c.created_at.isoformat()} for c in crises.scalars().all()],
        "notes": [{"id": str(n.id), "content": n.content, "type": n.note_type, "date": n.created_at.isoformat()} for n in notes.scalars().all()],
    }


async def generate_ai_summary(db: AsyncSession, patient_id) -> AIGeneratedSummary:
    timeline = await get_patient_timeline(db, patient_id)
    scores = timeline.get("stress_scores", [])
    crises = timeline.get("crisis_events", [])
    moods = timeline.get("mood_entries", [])

    # Analyze trends
    observations = []
    recommendations = []
    risk = "low"

    if scores:
        latest = scores[0]["score"]
        if len(scores) > 1:
            prev = scores[1]["score"]
            if latest > prev:
                observations.append(f"Stress score increased from {prev:.1f} to {latest:.1f}")
            elif latest < prev:
                observations.append(f"Stress score improved from {prev:.1f} to {latest:.1f}")
        observations.append(f"Current stress level: {scores[0]['category'].replace('_', ' ').title()} ({latest:.1f}/10)")

        if latest >= 7.0:
            risk = "high"
            recommendations.append("Consider increasing session frequency")
        elif latest >= 4.5:
            risk = "moderate"

    if crises:
        observations.append(f"{len(crises)} crisis events recorded")
        risk = "high"
        recommendations.append("Review crisis intervention plan")

    if not recommendations:
        recommendations.append("Continue current treatment plan")
        recommendations.append("Monitor mood patterns for emerging trends")

    summary = f"Patient assessment summary based on {len(scores)} stress scores, {len(moods)} mood entries, and {len(crises)} crisis events. "
    if risk == "high":
        summary += "Elevated risk level detected — close monitoring recommended."
    elif risk == "moderate":
        summary += "Moderate stress levels — regular follow-up advised."
    else:
        summary += "Stable condition — maintain current approach."

    return AIGeneratedSummary(
        patient_id=patient_id,
        summary=summary,
        key_observations=observations or ["Insufficient data for detailed analysis"],
        recommendations=recommendations,
        risk_level=risk,
        generated_at=datetime.now(timezone.utc),
    )


async def create_note(db: AsyncSession, therapist_id, data: NoteCreate) -> TherapistNote:
    note = TherapistNote(
        therapist_id=therapist_id,
        patient_id=data.patient_id,
        content=data.content,
        note_type=data.note_type,
    )
    db.add(note)
    await db.flush()
    await db.refresh(note)
    return note


async def get_patient_notes(db: AsyncSession, patient_id) -> list[TherapistNote]:
    result = await db.execute(
        select(TherapistNote)
        .where(TherapistNote.patient_id == patient_id)
        .order_by(desc(TherapistNote.created_at))
    )
    return list(result.scalars().all())


async def get_alerts(db: AsyncSession, therapist_id) -> list[dict]:
    result = await db.execute(
        select(PatientTherapistLink.patient_id)
        .where(PatientTherapistLink.therapist_id == therapist_id)
        .where(PatientTherapistLink.unlinked_at.is_(None))
    )
    patient_ids = [r[0] for r in result.all()]
    if not patient_ids:
        return []

    alerts = []
    for pid in patient_ids:
        # Recent crisis events
        crisis_result = await db.execute(
            select(CrisisEvent)
            .where(CrisisEvent.user_id == pid)
            .where(CrisisEvent.created_at >= datetime.now(timezone.utc) - timedelta(days=7))
        )
        for c in crisis_result.scalars().all():
            patient_result = await db.execute(select(User).where(User.id == pid))
            patient = patient_result.scalar_one_or_none()
            alerts.append({
                "patient_id": str(pid),
                "patient_name": patient.full_name if patient else "Unknown",
                "alert_type": "crisis_event",
                "severity": c.severity.value,
                "message": f"Crisis event ({c.severity.value}) triggered via {c.trigger_source}",
                "created_at": c.created_at.isoformat(),
            })

        # Score increase
        score_result = await db.execute(
            select(StressScore)
            .where(StressScore.user_id == pid)
            .order_by(desc(StressScore.computed_at)).limit(2)
        )
        recent_scores = score_result.scalars().all()
        if len(recent_scores) >= 2 and recent_scores[0].fused_score - recent_scores[1].fused_score >= 2.0:
            patient_result = await db.execute(select(User).where(User.id == pid))
            patient = patient_result.scalar_one_or_none()
            alerts.append({
                "patient_id": str(pid),
                "patient_name": patient.full_name if patient else "Unknown",
                "alert_type": "score_increase",
                "severity": "warning",
                "message": f"Stress score increased by {recent_scores[0].fused_score - recent_scores[1].fused_score:.1f} points",
                "created_at": recent_scores[0].computed_at.isoformat(),
            })

    return alerts
