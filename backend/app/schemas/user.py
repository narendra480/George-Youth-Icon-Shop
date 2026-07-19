from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserResponse(UserBase):
    id: int
    first_name: str
    last_name: str
    phone: str | None = None
    profile_image: str | None = None
    is_active: bool
    is_superuser: bool
    email_verified: bool
    last_login: datetime | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
