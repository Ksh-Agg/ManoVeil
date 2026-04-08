from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.permissions import get_current_user
from app.models.user import User
from app.schemas.stress import StressScoreRead, SHAPExplanation
from app.services import stress_service

router = APIRouter()


@router.get("/current", response_model=StressScoreRead | None)
async def get_current_score(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    score = await stress_service.get_latest_score(db, user.id)
    return StressScoreRead.model_validate(score) if score else None


@router.get("/history", response_model=list[StressScoreRead])
async def get_history(
    days: int = Query(30, ge=1, le=365),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    scores = await stress_service.get_stress_history(db, user.id, days)
    return [StressScoreRead.model_validate(s) for s in scores]


@router.get("/{score_id}/shap", response_model=SHAPExplanation)
async def get_shap(score_id: UUID, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    explanation = await stress_service.get_shap_explanation(db, score_id)
    if not explanation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="SHAP explanation not found")
    return explanation


@router.post("/compute", response_model=StressScoreRead)
async def compute_score(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    score = await stress_service.compute_stress_score(db, user.id)
    return StressScoreRead.model_validate(score)
