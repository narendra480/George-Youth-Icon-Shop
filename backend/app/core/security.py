from datetime import datetime, timedelta
import hashlib
import logging
import re
import secrets
from typing import Any, Optional, List, Dict

import bcrypt
from jose import JWTError, jwt

from app.core.config import settings

ALGORITHM = "HS256"
logger = logging.getLogger("app.security")


def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed_password: str) -> bool:
    result = bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))
    if not result:
        logger.warning("PASSWORD_VERIFICATION | Failed - Invalid password")
    return result


def generate_secure_token(length: int = 32) -> str:
    return secrets.token_urlsafe(length)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def validate_password_strength(password: str) -> None:
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long")
    if not re.search(r"[A-Z]", password):
        raise ValueError("Password must contain an uppercase letter")
    if not re.search(r"[a-z]", password):
        raise ValueError("Password must contain a lowercase letter")
    if not re.search(r"\d", password):
        raise ValueError("Password must contain a digit")
    if not re.search(r"[^A-Za-z0-9]", password):
        raise ValueError("Password must contain a special character")


def create_access_token(
    subject: str,
    roles: Optional[List[Dict[str, Any]]] = None,
    permissions: Optional[List[Dict[str, Any]]] = None,
    expires_delta: timedelta | None = None,
) -> str:
    """
    Create JWT access token with embedded roles and permissions.
    
    Args:
        subject: User ID or identifier
        roles: List of role dicts with id, name, slug
        permissions: List of permission dicts with id, name, slug
        expires_delta: Custom expiration time
    """
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.access_token_expires_minutes))
    payload: dict[str, Any] = {
        "sub": subject,
        "exp": expire,
        "roles": roles or [],
        "permissions": permissions or [],
    }
    token = jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)
    logger.debug(f"TOKEN_CREATED | Access token created for subject: {subject} with {len(roles or [])} roles")
    return token


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode JWT token and return full payload including roles/permissions.
    
    Returns:
        Dictionary with token payload or None if invalid
    """
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        logger.debug(f"TOKEN_DECODED | Valid token decoded for subject: {payload.get('sub')}")
        return payload
    except JWTError as exc:
        logger.warning(f"TOKEN_DECODE_ERROR | Invalid token - {str(exc)}")
        return None
