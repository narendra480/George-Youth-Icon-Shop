"""
Authorization dependencies for FastAPI endpoints.
Handles role and permission-based access control.
"""
import logging
from typing import Optional, List
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.session import get_db
from app.repositories.rbac_repository import UserRoleRepository
from app.repositories.user_repository import UserRepository

logger = logging.getLogger("app.authz")


class TokenPayload:
    """Parsed JWT token with roles and permissions"""
    def __init__(self, subject: str, roles: List[dict], permissions: List[dict]):
        self.subject = subject
        self.roles = roles
        self.permissions = permissions
        self.role_slugs = [r.get("slug") for r in roles]
        self.permission_slugs = [p.get("slug") for p in permissions]


def get_token_payload(token: str) -> TokenPayload:
    """Parse and validate JWT token"""
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return TokenPayload(
        subject=payload.get("sub"),
        roles=payload.get("roles", []),
        permissions=payload.get("permissions", []),
    )


def require_authentication(
    token: str = None,
    db: Session = Depends(get_db),
) -> dict:
    """
    Dependency for authenticated endpoints.
    Requires valid JWT token.
    Returns user data with embedded roles/permissions.
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    payload = decode_access_token(token)
    if not payload:
        logger.warning(f"AUTHZ | AUTH_FAILED | Invalid token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    user_repo = UserRepository(db)
    user = user_repo.get_by_id(int(user_id))
    
    if not user:
        logger.warning(f"AUTHZ | USER_NOT_FOUND | User id: {user_id}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        logger.warning(f"AUTHZ | USER_INACTIVE | User id: {user_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )
    
    logger.debug(f"AUTHZ | AUTH_SUCCESS | User: {user.email}")
    
    return {
        "user": user,
        "token_payload": TokenPayload(
            subject=str(user.id),
            roles=payload.get("roles", []),
            permissions=payload.get("permissions", []),
        ),
    }


def require_permission(required_permission: str):
    """
    Dependency factory for permission-based access control.
    
    Usage:
        @router.get("/admin/users")
        def list_users(auth=Depends(require_permission("users.view"))):
            ...
    """
    def permission_checker(
        auth: dict = Depends(require_authentication),
    ):
        permission_slugs = auth["token_payload"].permission_slugs
        
        if required_permission not in permission_slugs:
            logger.warning(
                f"AUTHZ | PERMISSION_DENIED | User: {auth['user'].email}, "
                f"Required: {required_permission}, Has: {permission_slugs}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required permission: {required_permission}",
            )
        
        logger.debug(
            f"AUTHZ | PERMISSION_GRANTED | User: {auth['user'].email}, "
            f"Permission: {required_permission}"
        )
        return auth
    
    return permission_checker


def require_role(required_role: str):
    """
    Dependency factory for role-based access control.
    
    Usage:
        @router.delete("/admin/users/{user_id}")
        def delete_user(user_id: int, auth=Depends(require_role("admin"))):
            ...
    """
    def role_checker(
        auth: dict = Depends(require_authentication),
    ):
        role_slugs = auth["token_payload"].role_slugs
        
        if required_role not in role_slugs:
            logger.warning(
                f"AUTHZ | ROLE_DENIED | User: {auth['user'].email}, "
                f"Required: {required_role}, Has: {role_slugs}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required role: {required_role}",
            )
        
        logger.debug(
            f"AUTHZ | ROLE_GRANTED | User: {auth['user'].email}, "
            f"Role: {required_role}"
        )
        return auth
    
    return role_checker


def require_any_role(*roles: str):
    """
    Dependency factory for role-based access with multiple allowed roles.
    
    Usage:
        @router.get("/dashboard")
        def dashboard(auth=Depends(require_any_role("admin", "manager"))):
            ...
    """
    def role_checker(
        auth: dict = Depends(require_authentication),
    ):
        role_slugs = auth["token_payload"].role_slugs
        
        if not any(role in role_slugs for role in roles):
            logger.warning(
                f"AUTHZ | ROLE_DENIED | User: {auth['user'].email}, "
                f"Required any of: {roles}, Has: {role_slugs}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient role level",
            )
        
        logger.debug(
            f"AUTHZ | ROLE_GRANTED | User: {auth['user'].email}, "
            f"Matched roles: {[r for r in roles if r in role_slugs]}"
        )
        return auth
    
    return role_checker


def require_any_permission(*permissions: str):
    """
    Dependency factory for permission-based access with multiple allowed permissions.
    
    Usage:
        @router.post("/products")
        def create_product(auth=Depends(require_any_permission("products.create", "admin.all"))):
            ...
    """
    def permission_checker(
        auth: dict = Depends(require_authentication),
    ):
        permission_slugs = auth["token_payload"].permission_slugs
        
        if not any(perm in permission_slugs for perm in permissions):
            logger.warning(
                f"AUTHZ | PERMISSION_DENIED | User: {auth['user'].email}, "
                f"Required any of: {permissions}, Has: {permission_slugs}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions",
            )
        
        logger.debug(
            f"AUTHZ | PERMISSION_GRANTED | User: {auth['user'].email}, "
            f"Matched permissions: {[p for p in permissions if p in permission_slugs]}"
        )
        return auth
    
    return permission_checker
