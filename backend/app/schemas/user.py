from datetime import date, datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field
from app.models.user import AgeGroup, UserRole, Persona


class UserCreate(BaseModel):
    email: str = Field(..., max_length=255)
    password: str = Field(..., min_length=8, max_length=128)
    full_name: str = Field(..., min_length=1, max_length=255)
    date_of_birth: date
    age_group: AgeGroup
    role: UserRole = UserRole.USER
    emergency_contact_name: str | None = None
    emergency_contact_phone: str | None = None


class UserRead(BaseModel):
    id: UUID
    email: str
    full_name: str
    date_of_birth: date
    age_group: AgeGroup
    role: UserRole
    persona: Persona
    emergency_contact_name: str | None
    emergency_contact_phone: str | None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    full_name: str | None = None
    emergency_contact_name: str | None = None
    emergency_contact_phone: str | None = None


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserRead


class LoginRequest(BaseModel):
    email: str
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str
