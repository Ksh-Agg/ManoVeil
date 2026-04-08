from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.permissions import require_role
from app.models.user import User, UserRole
from app.services import analytics_service

router = APIRouter()

admin_dep = require_role(UserRole.ADMIN)


@router.get("/stats")
async def platform_stats(user: User = Depends(admin_dep), db: AsyncSession = Depends(get_db)):
    return await analytics_service.get_platform_stats(db)


@router.get("/users")
async def list_users(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    user: User = Depends(admin_dep),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).limit(limit).offset(offset))
    users = result.scalars().all()
    total = (await db.execute(select(func.count(User.id)))).scalar()
    return {"total": total, "users": [{"id": str(u.id), "email": u.email, "name": u.full_name, "role": u.role.value, "age_group": u.age_group.value, "persona": u.persona.value, "active": u.is_active} for u in users]}


@router.patch("/users/{user_id}/role")
async def change_role(user_id: UUID, role: UserRole, admin: User = Depends(admin_dep), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user_id))
    target = result.scalar_one_or_none()
    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    target.role = role
    await db.flush()
    return {"status": "updated", "user_id": str(user_id), "new_role": role.value}
