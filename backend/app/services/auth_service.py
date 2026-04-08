from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User, UserRole, AGE_TO_PERSONA, Persona
from app.schemas.user import UserCreate, TokenPair, UserRead
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token
from app.core.exceptions import ConflictError, BadRequestError


async def register_user(db: AsyncSession, data: UserCreate) -> User:
    result = await db.execute(select(User).where(User.email == data.email))
    if result.scalar_one_or_none():
        raise ConflictError("Email already registered")

    persona = Persona.MANOCONNECT if data.role == UserRole.THERAPIST else AGE_TO_PERSONA.get(data.age_group)
    if not persona:
        raise BadRequestError("Invalid age group")

    user = User(
        email=data.email,
        hashed_password=hash_password(data.password),
        full_name=data.full_name,
        date_of_birth=data.date_of_birth,
        age_group=data.age_group,
        role=data.role,
        persona=persona,
        emergency_contact_name=data.emergency_contact_name,
        emergency_contact_phone=data.emergency_contact_phone,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


async def authenticate_user(db: AsyncSession, email: str, password: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


async def authenticate_by_id(db: AsyncSession, user_id: str) -> User | None:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


def create_tokens(user: User) -> TokenPair:
    access = create_access_token({"sub": str(user.id), "role": user.role.value})
    refresh = create_refresh_token({"sub": str(user.id)})
    return TokenPair(
        access_token=access,
        refresh_token=refresh,
        user=UserRead.model_validate(user),
    )
