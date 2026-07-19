from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.session import get_db
from app.repositories.user_repository import UserRepository
from app.schemas.auth import (
    AccessTokenResponse,
    ChangePasswordRequest,
    ForgotPasswordRequest,
    LoginRequest,
    LogoutRequest,
    RegisterRequest,
    RefreshRequest,
    ResetPasswordRequest,
    TokenResponse,
    VerifyEmailRequest,
)
from app.schemas.response import ApiResponse
from app.schemas.user import UserResponse
from app.services.auth_service import AuthService
from app.services.email_service import get_email_service

router = APIRouter(tags=["Authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    email_service = get_email_service()
    return AuthService(db, email_service)


@router.post("/register", response_model=ApiResponse[UserResponse])
def register_user(payload: RegisterRequest, auth_service: AuthService = Depends(get_auth_service)) -> ApiResponse[UserResponse]:
    try:
        user = auth_service.register_user(payload)
        return ApiResponse(success=True, message="User registered successfully", data=user)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.post("/login", response_model=ApiResponse[TokenResponse])
def login(payload: LoginRequest, auth_service: AuthService = Depends(get_auth_service)) -> ApiResponse[TokenResponse]:
    try:
        token = auth_service.login(payload)
        return ApiResponse(success=True, message="Login successful", data=token)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))


@router.post("/refresh", response_model=ApiResponse[AccessTokenResponse])
def refresh(payload: RefreshRequest, auth_service: AuthService = Depends(get_auth_service)) -> ApiResponse[AccessTokenResponse]:
    try:
        token = auth_service.refresh_access_token(payload)
        return ApiResponse(success=True, message="Access token refreshed", data=token)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))


@router.post("/logout", response_model=ApiResponse[None])
def logout(payload: LogoutRequest, auth_service: AuthService = Depends(get_auth_service)) -> ApiResponse[None]:
    auth_service.logout(payload)
    return ApiResponse(success=True, message="Logout successful")


@router.get("/me", response_model=ApiResponse[UserResponse])
def read_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> ApiResponse[UserResponse]:
    user_id = decode_access_token(token)
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalid or expired")
    user = UserRepository(db).get_by_id(int(user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return ApiResponse(success=True, message="Current user fetched", data=user)


@router.post("/forgot-password", response_model=ApiResponse[None])
def forgot_password(payload: ForgotPasswordRequest, auth_service: AuthService = Depends(get_auth_service)) -> ApiResponse[None]:
    auth_service.forgot_password(payload)
    return ApiResponse(success=True, message="If this email exists, password reset instructions have been sent")


@router.post("/reset-password", response_model=ApiResponse[None])
def reset_password(payload: ResetPasswordRequest, auth_service: AuthService = Depends(get_auth_service)) -> ApiResponse[None]:
    try:
        auth_service.reset_password(payload)
        return ApiResponse(success=True, message="Password reset successfully")
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.post("/change-password", response_model=ApiResponse[None])
def change_password(
    payload: ChangePasswordRequest,
    token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service),
) -> ApiResponse[None]:
    user_id = decode_access_token(token)
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalid or expired")
    try:
        auth_service.change_password(int(user_id), payload)
        return ApiResponse(success=True, message="Password changed successfully")
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.post("/verify-email", response_model=ApiResponse[UserResponse])
def verify_email(payload: VerifyEmailRequest, auth_service: AuthService = Depends(get_auth_service)) -> ApiResponse[UserResponse]:
    try:
        user = auth_service.verify_email(payload)
        return ApiResponse(success=True, message="Email verified successfully", data=user)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
