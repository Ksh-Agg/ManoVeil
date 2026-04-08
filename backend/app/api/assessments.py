from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.permissions import get_current_user
from app.models.user import User
from app.models.assessment import AssessmentType
from app.schemas.assessment import AssessmentCreate, AssessmentRead, InstrumentInfo
from app.services import assessment_service

router = APIRouter()


@router.get("/instruments", response_model=list[InstrumentInfo])
async def list_instruments(user: User = Depends(get_current_user)):
    return assessment_service.get_eligible_instruments(user.age_group)


@router.get("/instruments/{assessment_type}/questions", response_model=InstrumentInfo)
async def get_questions(assessment_type: AssessmentType, user: User = Depends(get_current_user)):
    return assessment_service.get_instrument_questions(assessment_type)


@router.post("/", response_model=AssessmentRead, status_code=status.HTTP_201_CREATED)
async def submit_assessment(
    data: AssessmentCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await assessment_service.create_assessment(db, user.id, data)
    return AssessmentRead.model_validate(result)


@router.get("/", response_model=list[AssessmentRead])
async def list_assessments(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    results = await assessment_service.get_user_assessments(db, user.id, limit, offset)
    return [AssessmentRead.model_validate(a) for a in results]


@router.get("/{assessment_id}", response_model=AssessmentRead)
async def get_assessment(
    assessment_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await assessment_service.get_assessment_by_id(db, assessment_id)
    if not result or result.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found")
    return AssessmentRead.model_validate(result)
