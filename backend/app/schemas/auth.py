from datetime import datetime
from typing import Generic, Optional, TypeVar

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator

from app.core.security import validate_password_strength


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)


class RegisterRequest(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=128)
    last_name: str = Field(..., min_length=1, max_length=128)
    email: EmailStr
    phone: Optional[str] = None
    password: str = Field(..., min_length=8)
    confirm_password: str = Field(..., min_length=8)

    @field_validator("password")
    def validate_password(cls, value: str) -> str:
        validate_password_strength(value)
        return value

    @field_validator("phone")
    def validate_phone(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        digits = "".join([c for c in value if c.isdigit()])
        if not digits:
            raise ValueError("Phone must contain digits only")
        if len(digits) < 10 or len(digits) > 15:
            raise ValueError("Phone must be between 10 and 15 digits")
        return digits

    @model_validator(mode="after")
    def validate_passwords_match(self) -> "RegisterRequest":
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

    class Config:
        from_attributes = True


class AccessTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

    class Config:
        from_attributes = True


class RefreshRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    password: str = Field(..., min_length=8)
    confirm_password: str = Field(..., min_length=8)

    @field_validator("password")
    def validate_password(cls, value: str) -> str:
        validate_password_strength(value)
        return value

    @model_validator(mode="after")
    def validate_passwords_match(self) -> "ResetPasswordRequest":
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self


class ChangePasswordRequest(BaseModel):
    old_password: str = Field(..., min_length=8)
    new_password: str = Field(..., min_length=8)
    confirm_password: str = Field(..., min_length=8)

    @field_validator("new_password")
    def validate_password(cls, value: str) -> str:
        validate_password_strength(value)
        return value

    @model_validator(mode="after")
    def validate_passwords_match(self) -> "ChangePasswordRequest":
        if self.new_password != self.confirm_password:
            raise ValueError("New password and confirmation must match")
        return self


class VerifyEmailRequest(BaseModel):
    token: str


DataT = TypeVar("DataT")


class ApiResponse(BaseModel, Generic[DataT]):
    success: bool
    message: str
    data: Optional[DataT] = None
    errors: Optional[list[str]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True