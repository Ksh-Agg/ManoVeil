from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.permissions import require_role
from app.models.user import User, UserRole
from app.schemas.therapist import NoteCreate, NoteRead, LinkPatientRequest, PatientSummary, AIGeneratedSummary
from app.services import therapist_service

router = APIRouter()

therapist_dep = require_role(UserRole.THERAPIST, UserRole.ADMIN)


@router.get("/patients", response_model=list[PatientSummary])
async def list_patients(user: User = Depends(therapist_dep), db: AsyncSession = Depends(get_db)):
    return await therapist_service.get_linked_patients(db, user.id)


@router.post("/patients/link", status_code=201)
async def link_patient(data: LinkPatientRequest, user: User = Depends(therapist_dep), db: AsyncSession = Depends(get_db)):
    link = await therapist_service.link_patient(db, user.id, data.patient_id, data.is_primary)
    return {"status": "linked", "id": str(link.id)}


@router.get("/patients/{patient_id}/timeline")
async def patient_timeline(patient_id: UUID, user: User = Depends(therapist_dep), db: AsyncSession = Depends(get_db)):
    return await therapist_service.get_patient_timeline(db, patient_id)


@router.get("/patients/{patient_id}/summary", response_model=AIGeneratedSummary)
async def patient_summary(patient_id: UUID, user: User = Depends(therapist_dep), db: AsyncSession = Depends(get_db)):
    return await therapist_service.generate_ai_summary(db, patient_id)


@router.post("/notes", response_model=NoteRead, status_code=201)
async def create_note(data: NoteCreate, user: User = Depends(therapist_dep), db: AsyncSession = Depends(get_db)):
    note = await therapist_service.create_note(db, user.id, data)
    return NoteRead(
        id=note.id, therapist_id=note.therapist_id, patient_id=note.patient_id,
        content=note.content, note_type=note.note_type,
        created_at=note.created_at, updated_at=note.updated_at,
        therapist_name=user.full_name,
    )


@router.get("/notes", response_model=list[NoteRead])
async def list_notes(patient_id: UUID = Query(...), user: User = Depends(therapist_dep), db: AsyncSession = Depends(get_db)):
    notes = await therapist_service.get_patient_notes(db, patient_id)
    return [NoteRead(
        id=n.id, therapist_id=n.therapist_id, patient_id=n.patient_id,
        content=n.content, note_type=n.note_type,
        created_at=n.created_at, updated_at=n.updated_at,
    ) for n in notes]


@router.get("/alerts")
async def get_alerts(user: User = Depends(therapist_dep), db: AsyncSession = Depends(get_db)):
    return await therapist_service.get_alerts(db, user.id)


@router.get("/analytics")
async def get_analytics(user: User = Depends(therapist_dep), db: AsyncSession = Depends(get_db)):
    from app.services import analytics_service
    return await analytics_service.get_platform_stats(db)
