from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.permissions import get_current_user
from app.models.user import User
from app.schemas.intervention import InterventionRead, CompletionCreate, CompletionRead
from app.services import intervention_service, stress_service

router = APIRouter()


@router.get("/", response_model=list[InterventionRead])
async def list_interventions(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    latest = await stress_service.get_latest_score(db, user.id)
    category = latest.category if latest else None
    results = await intervention_service.get_recommended_interventions(db, user.persona, category)
    return [InterventionRead.model_validate(i) for i in results]


@router.get("/{intervention_id}", response_model=InterventionRead)
async def get_intervention(intervention_id: UUID, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await intervention_service.get_intervention_by_id(db, intervention_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Intervention not found")
    return InterventionRead.model_validate(result)


@router.post("/{intervention_id}/complete", response_model=CompletionRead, status_code=201)
async def complete(intervention_id: UUID, data: CompletionCreate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await intervention_service.complete_intervention(db, user.id, intervention_id, data)
    return CompletionRead.model_validate(result)


@router.get("/history/completions", response_model=list[CompletionRead])
async def completion_history(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    results = await intervention_service.get_completion_history(db, user.id)
    return [CompletionRead.model_validate(c) for c in results]
