from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.permissions import get_current_user, require_role
from app.models.user import User, UserRole
from app.schemas.blockchain import GradientSubmission, GradientCommitRead, FederatedRoundRead, BAFLStatus
from app.services import blockchain_service

router = APIRouter()


@router.get("/status", response_model=BAFLStatus)
async def bafl_status(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await blockchain_service.get_bafl_status(db)


@router.post("/gradients", response_model=GradientCommitRead, status_code=201)
async def submit_gradient(data: GradientSubmission, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    commit = await blockchain_service.submit_gradient(db, data)
    return GradientCommitRead.model_validate(commit)


@router.get("/rounds", response_model=list[FederatedRoundRead])
async def list_rounds(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    rounds = await blockchain_service.get_all_rounds(db)
    return [FederatedRoundRead.model_validate(r) for r in rounds]


@router.get("/rounds/{round_id}", response_model=FederatedRoundRead)
async def get_round(round_id: UUID, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    from sqlalchemy import select
    from app.models.blockchain import FederatedRound
    result = await db.execute(select(FederatedRound).where(FederatedRound.id == round_id))
    r = result.scalar_one_or_none()
    if not r:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Round not found")
    return FederatedRoundRead.model_validate(r)


@router.post("/rounds/start", response_model=FederatedRoundRead, status_code=201)
async def start_round(model_version: str = "v1.0", admin: User = Depends(require_role(UserRole.ADMIN)), db: AsyncSession = Depends(get_db)):
    r = await blockchain_service.start_new_round(db, model_version)
    return FederatedRoundRead.model_validate(r)


@router.post("/rounds/{round_id}/complete", response_model=FederatedRoundRead)
async def complete_round(round_id: UUID, admin: User = Depends(require_role(UserRole.ADMIN)), db: AsyncSession = Depends(get_db)):
    r = await blockchain_service.complete_round(db, round_id)
    if not r:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Round not found")
    return FederatedRoundRead.model_validate(r)
