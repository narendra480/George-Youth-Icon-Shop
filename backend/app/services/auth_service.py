from datetime import datetime, timedelta
import logging
from typing import Optional, Dict, Any

from jose import JWTError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import (
    create_access_token,
    decode_access_token,
    generate_secure_token,
    get_password_hash,
    hash_token,
    verify_password,
)
from app.db.models import User
from app.repositories.token_repository import TokenRepository
from app.repositories.user_repository import UserRepository
from app.schemas.auth import (
    AccessTokenResponse,
    ChangePasswordRequest,
    ForgotPasswordRequest,
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    ResetPasswordRequest,
    TokenResponse,
    VerifyEmailRequest,
)
from app.services.email_service import EmailService

logger = logging.getLogger("app.auth_service")


class AuthService:
    def __init__(self, db: Session, email_service: EmailService) -> None:
        self.db = db
        self.user_repository = UserRepository(db)
        self.token_repository = TokenRepository(db)
        self.email_service = email_service

    def register_user(self, payload: RegisterRequest) -> User:
        email = payload.email.lower().strip()
        logger.info(f"AUTH | REGISTER | Attempting registration for email: {email}")
        
        if self.user_repository.get_by_email(email):
            logger.warning(f"AUTH | REGISTER | Failed - Email already registered: {email}")
            raise ValueError("Email already registered")

        phone_val = None
        if payload.phone:
            # sanitize phone to digits-only
            phone_val = "".join([c for c in payload.phone if c.isdigit()])
            if self.user_repository.get_by_phone(phone_val):
                logger.warning(f"AUTH | REGISTER | Failed - Phone already registered: {phone_val}")
                raise ValueError("Phone already registered")

        verification_token = generate_secure_token()
        user = User(
            first_name=payload.first_name.strip(),
            last_name=payload.last_name.strip(),
            email=email,
            phone=phone_val,
            hashed_password=get_password_hash(payload.password),
            verification_token=hash_token(verification_token),
            is_active=False,
            is_superuser=False,
            email_verified=False,
        )

        try:
            # transactional save
            self.user_repository.add(user)
            self.db.commit()
            self.db.refresh(user)
            logger.info(f"AUTH | REGISTER | Success - User registered: {email} (ID: {user.id})")
        except Exception as exc:
            self.db.rollback()
            logger.error(f"AUTH | REGISTER | Error - Failed to save user: {email}", exc_info=True)
            raise ValueError("Failed to register user") from exc

        # send verification email after commit
        try:
            self.email_service.send_verification_email(user.email, verification_token)
            logger.info(f"AUTH | EMAIL | Verification email sent to: {email}")
        except Exception as exc:
            logger.warning(f"AUTH | EMAIL | Failed to send verification email to: {email}", exc_info=True)
        
        return user

    def login(self, payload: LoginRequest) -> TokenResponse:
        email = payload.email.lower().strip()
        logger.info(f"AUTH | LOGIN | Attempting login for email: {email}")
        
        user = self.user_repository.get_by_email(email)
        if not user:
            logger.warning(f"AUTH | LOGIN | Failed - User not found: {email}")
            raise ValueError("Invalid credentials")
        
        if not verify_password(payload.password, user.hashed_password):
            logger.warning(f"AUTH | LOGIN | Failed - Invalid password for user: {email}")
            raise ValueError("Invalid credentials")
        
        if not user.is_active:
            logger.warning(f"AUTH | LOGIN | Failed - Account not active: {email}")
            raise ValueError("Account is not active")

        access_token = create_access_token(subject=str(user.id))
        refresh_token = generate_secure_token()
        refreshed_expires = datetime.utcnow() + timedelta(days=settings.refresh_token_expires_days)
        self.token_repository.create(user.id, refresh_token, refreshed_expires)

        user.last_login = datetime.utcnow()
        self.user_repository.save(user)

        logger.info(f"AUTH | LOGIN | Success - User logged in: {email} (ID: {user.id})")
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.access_token_expires_minutes * 60,
        )

    def refresh_access_token(self, payload: RefreshRequest) -> AccessTokenResponse:
        logger.debug("AUTH | REFRESH | Attempting to refresh access token")
        
        refresh_token = self.token_repository.get_valid_token(payload.refresh_token)
        if not refresh_token:
            logger.warning("AUTH | REFRESH | Failed - Invalid or expired refresh token")
            raise ValueError("Refresh token invalid")

        access_token = create_access_token(subject=str(refresh_token.user_id))
        logger.info(f"AUTH | REFRESH | Success - Token refreshed for user ID: {refresh_token.user_id}")
        
        return AccessTokenResponse(
            access_token=access_token,
            expires_in=settings.access_token_expires_minutes * 60,
        )

    def logout(self, payload: RefreshRequest) -> None:
        logger.info("AUTH | LOGOUT | Attempting logout")
        self.token_repository.revoke(payload.refresh_token)
        logger.info("AUTH | LOGOUT | Success - User logged out")

    def get_current_user(self, token: str) -> User:
        user_id = decode_access_token(token)
        if not user_id:
            logger.warning("AUTH | GET_CURRENT | Failed - Invalid or expired token")
            raise ValueError("Token invalid or expired")
        user = self.user_repository.get_by_id(int(user_id))
        if not user:
            logger.warning(f"AUTH | GET_CURRENT | Failed - User not found: ID {user_id}")
            raise ValueError("User not found")
        logger.debug(f"AUTH | GET_CURRENT | Success - Retrieved user: ID {user_id}")
        return user

    def forgot_password(self, payload: ForgotPasswordRequest) -> None:
        email = payload.email.lower().strip()
        logger.info(f"AUTH | FORGOT_PASSWORD | Attempting password reset for: {email}")
        
        user = self.user_repository.get_by_email(email)
        if not user:
            logger.info(f"AUTH | FORGOT_PASSWORD | Email not found (silent fail): {email}")
            return
        
        reset_token = generate_secure_token()
        user.password_reset_token = hash_token(reset_token)
        user.password_reset_expiry = datetime.utcnow() + timedelta(hours=settings.password_reset_token_expires_hours)
        self.user_repository.save(user)
        
        try:
            self.email_service.send_password_reset_email(user.email, reset_token)
            logger.info(f"AUTH | FORGOT_PASSWORD | Success - Reset email sent to: {email}")
        except Exception as exc:
            logger.warning(f"AUTH | FORGOT_PASSWORD | Failed to send reset email to: {email}", exc_info=True)

    def reset_password(self, payload: ResetPasswordRequest) -> None:
        logger.info("AUTH | RESET_PASSWORD | Attempting password reset with token")
        
        hashed_token = hash_token(payload.token)
        user = self.user_repository.get_by_password_reset_token(hashed_token)
        if not user or not user.password_reset_expiry or user.password_reset_expiry < datetime.utcnow():
            logger.warning("AUTH | RESET_PASSWORD | Failed - Invalid or expired reset token")
            raise ValueError("Reset token invalid or expired")
        
        user.hashed_password = get_password_hash(payload.password)
        user.password_reset_token = None
        user.password_reset_expiry = None
        self.user_repository.save(user)
        logger.info(f"AUTH | RESET_PASSWORD | Success - Password reset for user: ID {user.id}")

    def change_password(self, user_id: int, payload: ChangePasswordRequest) -> None:
        logger.info(f"AUTH | CHANGE_PASSWORD | Attempting password change for user: ID {user_id}")
        
        user = self.user_repository.get_by_id(user_id)
        if not user:
            logger.warning(f"AUTH | CHANGE_PASSWORD | Failed - User not found: ID {user_id}")
            raise ValueError("User not found")
        if not verify_password(payload.old_password, user.hashed_password):
            logger.warning(f"AUTH | CHANGE_PASSWORD | Failed - Old password incorrect for user: ID {user_id}")
            raise ValueError("Old password is incorrect")
        user.hashed_password = get_password_hash(payload.new_password)
        self.user_repository.save(user)
        logger.info(f"AUTH | CHANGE_PASSWORD | Success - Password changed for user: ID {user_id}")

    def verify_email(self, payload: VerifyEmailRequest) -> User:
        logger.info("AUTH | VERIFY_EMAIL | Attempting email verification with token")
        
        user = self.user_repository.get_by_verification_token(hash_token(payload.token))
        if not user:
            logger.warning("AUTH | VERIFY_EMAIL | Failed - Invalid verification token")
            raise ValueError("Verification token invalid")
        user.email_verified = True
        user.is_active = True
        user.verification_token = None
        saved_user = self.user_repository.save(user)
        logger.info(f"AUTH | VERIFY_EMAIL | Success - Email verified for user: {user.email} (ID: {user.id})")
        return saved_user
    def __init__(self, db: Session, email_service: EmailService) -> None:
        self.db = db
        self.user_repository = UserRepository(db)
        self.token_repository = TokenRepository(db)
        self.email_service = email_service

    def register_user(self, payload: RegisterRequest) -> User:
        if self.user_repository.get_by_email(payload.email.lower().strip()):
            raise ValueError("Email already registered")

        phone_val = None
        if payload.phone:
            # sanitize phone to digits-only
            phone_val = "".join([c for c in payload.phone if c.isdigit()])
            if self.user_repository.get_by_phone(phone_val):
                raise ValueError("Phone already registered")

        verification_token = generate_secure_token()
        user = User(
            first_name=payload.first_name.strip(),
            last_name=payload.last_name.strip(),
            email=payload.email.lower().strip(),
            phone=phone_val,
            hashed_password=get_password_hash(payload.password),
            verification_token=hash_token(verification_token),
            is_active=False,
            is_superuser=False,
            email_verified=False,
        )

        try:
            # transactional save
            self.user_repository.add(user)
            self.db.commit()
            self.db.refresh(user)
        except Exception as exc:
            self.db.rollback()
            raise ValueError("Failed to register user") from exc

        # send verification email after commit
        self.email_service.send_verification_email(user.email, verification_token)
        return user

    def login(self, payload: LoginRequest) -> TokenResponse:
        user = self.user_repository.get_by_email(payload.email.lower().strip())
        if not user or not verify_password(payload.password, user.hashed_password):
            raise ValueError("Invalid credentials")
        if not user.is_active:
            raise ValueError("Account is not active")

        access_token = create_access_token(subject=str(user.id))
        refresh_token = generate_secure_token()
        refreshed_expires = datetime.utcnow() + timedelta(days=settings.refresh_token_expires_days)
        self.token_repository.create(user.id, refresh_token, refreshed_expires)

        user.last_login = datetime.utcnow()
        self.user_repository.save(user)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.access_token_expires_minutes * 60,
        )

    def refresh_access_token(self, payload: RefreshRequest) -> AccessTokenResponse:
        refresh_token = self.token_repository.get_valid_token(payload.refresh_token)
        if not refresh_token:
            raise ValueError("Refresh token invalid")

        access_token = create_access_token(subject=str(refresh_token.user_id))
        return AccessTokenResponse(
            access_token=access_token,
            expires_in=settings.access_token_expires_minutes * 60,
        )

    def logout(self, payload: RefreshRequest) -> None:
        self.token_repository.revoke(payload.refresh_token)

    def get_current_user(self, token: str) -> User:
        user_id = decode_access_token(token)
        if not user_id:
            raise ValueError("Token invalid or expired")
        user = self.user_repository.get_by_id(int(user_id))
        if not user:
            raise ValueError("User not found")
        return user

    def forgot_password(self, payload: ForgotPasswordRequest) -> None:
        user = self.user_repository.get_by_email(payload.email.lower().strip())
        if not user:
            return
        reset_token = generate_secure_token()
        user.password_reset_token = hash_token(reset_token)
        user.password_reset_expiry = datetime.utcnow() + timedelta(hours=settings.password_reset_token_expires_hours)
        self.user_repository.save(user)
        self.email_service.send_password_reset_email(user.email, reset_token)

    def reset_password(self, payload: ResetPasswordRequest) -> None:
        hashed_token = hash_token(payload.token)
        user = self.user_repository.get_by_password_reset_token(hashed_token)
        if not user or not user.password_reset_expiry or user.password_reset_expiry < datetime.utcnow():
            raise ValueError("Reset token invalid or expired")
        user.hashed_password = get_password_hash(payload.password)
        user.password_reset_token = None
        user.password_reset_expiry = None
        self.user_repository.save(user)

    def change_password(self, user_id: int, payload: ChangePasswordRequest) -> None:
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        if not verify_password(payload.old_password, user.hashed_password):
            raise ValueError("Old password is incorrect")
        user.hashed_password = get_password_hash(payload.new_password)
        self.user_repository.save(user)

    def verify_email(self, payload: VerifyEmailRequest) -> User:
        user = self.user_repository.get_by_verification_token(hash_token(payload.token))
        if not user:
            raise ValueError("Verification token invalid")
        user.email_verified = True
        user.is_active = True
        user.verification_token = None
        return self.user_repository.save(user)
