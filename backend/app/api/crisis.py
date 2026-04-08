from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.permissions import get_current_user
from app.models.user import User
from app.schemas.crisis import CrisisEventRead, CrisisResource
from app.services import crisis_service

router = APIRouter()


@router.post("/sos", response_model=CrisisEventRead, status_code=201)
async def trigger_sos(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    event = await crisis_service.trigger_sos(db, user.id)
    return CrisisEventRead.model_validate(event)


@router.get("/resources", response_model=list[CrisisResource])
async def get_resources(user: User = Depends(get_current_user)):
    return crisis_service.get_crisis_resources()


@router.get("/events", response_model=list[CrisisEventRead])
async def get_events(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    events = await crisis_service.get_user_crisis_events(db, user.id)
    return [CrisisEventRead.model_validate(e) for e in events]
