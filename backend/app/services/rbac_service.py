import logging
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from app.db.models import User, Permission, Role, UserRole
from app.repositories.rbac_repository import RoleRepository, PermissionRepository, UserRoleRepository
from app.repositories.user_repository import UserRepository

logger = logging.getLogger("app.rbac_service")


class RBACService:
    """Enterprise RBAC (Role-Based Access Control) Service"""

    def __init__(self, db: Session):
        self.db = db
        self.role_repo = RoleRepository(db)
        self.permission_repo = PermissionRepository(db)
        self.user_role_repo = UserRoleRepository(db)
        self.user_repo = UserRepository(db)

    # ========================================================================
    # Permission Management
    # ========================================================================
    def create_permission(
        self,
        name: str,
        slug: str,
        description: Optional[str] = None,
        category: str = "general",
        is_system: bool = False,
    ) -> Permission:
        """Create a new permission"""
        existing = self.permission_repo.get_by_slug(slug)
        if existing:
            logger.warning(f"RBAC | PERMISSION_EXISTS | Slug: {slug}")
            raise ValueError(f"Permission with slug '{slug}' already exists")

        return self.permission_repo.create(name, slug, description, category, is_system)

    def get_permission(self, permission_id: int) -> Optional[Permission]:
        """Get permission by ID"""
        return self.permission_repo.get_by_id(permission_id)

    def list_permissions(self, category: Optional[str] = None) -> List[Permission]:
        """List all permissions or filter by category"""
        if category:
            return self.permission_repo.list_by_category(category)
        return self.permission_repo.list_all()

    def update_permission(
        self,
        permission_id: int,
        name: Optional[str] = None,
        slug: Optional[str] = None,
        description: Optional[str] = None,
        category: Optional[str] = None,
    ) -> Optional[Permission]:
        """Update permission"""
        permission = self.permission_repo.get_by_id(permission_id)
        if not permission:
            return None

        if permission.is_system and (name or slug):
            logger.warning(f"RBAC | SYSTEM_PERMISSION_EDIT_DENIED | Permission id: {permission_id}")
            raise ValueError("Cannot modify system permissions")

        return self.permission_repo.update(permission_id, name, slug, description, category)

    def delete_permission(self, permission_id: int) -> bool:
        """Delete permission (not if system permission)"""
        return self.permission_repo.delete(permission_id)

    # ========================================================================
    # Role Management
    # ========================================================================
    def create_role(
        self,
        name: str,
        slug: str,
        description: Optional[str] = None,
        permission_ids: Optional[List[int]] = None,
        is_system: bool = False,
    ) -> Role:
        """Create a new role with optional permissions"""
        existing = self.role_repo.get_by_slug(slug)
        if existing:
            logger.warning(f"RBAC | ROLE_EXISTS | Slug: {slug}")
            raise ValueError(f"Role with slug '{slug}' already exists")

        role = self.role_repo.create(name, slug, description, is_system)

        if permission_ids:
            for perm_id in permission_ids:
                self.role_repo.assign_permission(role.id, perm_id)

        return role

    def get_role(self, role_id: int) -> Optional[Role]:
        """Get role by ID"""
        return self.role_repo.get_by_id(role_id)

    def list_roles(self) -> List[Role]:
        """List all roles"""
        return self.role_repo.list_all()

    def update_role(
        self,
        role_id: int,
        name: Optional[str] = None,
        slug: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Optional[Role]:
        """Update role"""
        role = self.role_repo.get_by_id(role_id)
        if not role:
            return None

        if role.is_system and (name or slug):
            logger.warning(f"RBAC | SYSTEM_ROLE_EDIT_DENIED | Role id: {role_id}")
            raise ValueError("Cannot modify system roles")

        return self.role_repo.update(role_id, name, slug, description)

    def delete_role(self, role_id: int) -> bool:
        """Delete role (not if system role)"""
        return self.role_repo.delete(role_id)

    def assign_permission_to_role(self, role_id: int, permission_id: int) -> bool:
        """Assign permission to role"""
        permission = self.permission_repo.get_by_id(permission_id)
        if not permission:
            raise ValueError(f"Permission {permission_id} not found")

        return self.role_repo.assign_permission(role_id, permission_id)

    def remove_permission_from_role(self, role_id: int, permission_id: int) -> bool:
        """Remove permission from role"""
        return self.role_repo.remove_permission(role_id, permission_id)

    def get_role_permissions(self, role_id: int) -> List[Permission]:
        """Get all permissions for a role"""
        return self.role_repo.get_permissions(role_id)

    # ========================================================================
    # User Role Management
    # ========================================================================
    def assign_role_to_user(
        self,
        user_id: int,
        role_id: int,
        assigned_by: Optional[int] = None,
        reason: Optional[str] = None,
    ) -> UserRole:
        """Assign role to user"""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")

        role = self.role_repo.get_by_id(role_id)
        if not role:
            raise ValueError(f"Role {role_id} not found")

        return self.user_role_repo.assign_role(user_id, role_id, assigned_by, reason)

    def remove_role_from_user(self, user_id: int, role_id: int) -> bool:
        """Remove role from user"""
        return self.user_role_repo.remove_role(user_id, role_id)

    def get_user_roles(self, user_id: int) -> List[Role]:
        """Get all roles for a user"""
        user_roles = self.user_role_repo.get_user_roles(user_id)
        return [ur.role for ur in user_roles]

    def get_user_permissions(self, user_id: int) -> List[Permission]:
        """Get all permissions for a user (flattened from all roles)"""
        roles = self.get_user_roles(user_id)
        permissions_set = set()
        permissions_dict = {}

        for role in roles:
            for permission in role.permissions:
                permissions_set.add(permission.id)
                permissions_dict[permission.id] = permission

        return [permissions_dict[pid] for pid in sorted(permissions_set)]

    def get_users_by_role(self, role_id: int) -> List[User]:
        """Get all users with a specific role"""
        user_roles = self.user_role_repo.get_role_users(role_id)
        return [ur.user for ur in user_roles]

    # ========================================================================
    # User Token Payload Helper
    # ========================================================================
    def get_user_token_payload(self, user_id: int) -> Dict[str, Any]:
        """
        Build token payload with roles and permissions for a user.
        Used during login/token refresh.
        """
        roles = self.get_user_roles(user_id)
        permissions = self.get_user_permissions(user_id)

        return {
            "roles": [{"id": r.id, "name": r.name, "slug": r.slug} for r in roles],
            "permissions": [{"id": p.id, "name": p.name, "slug": p.slug} for p in permissions],
        }

    # ========================================================================
    # Permission Check Helpers
    # ========================================================================
    def user_has_permission(self, user_id: int, permission_slug: str) -> bool:
        """Check if user has specific permission"""
        permissions = self.get_user_permissions(user_id)
        return any(p.slug == permission_slug for p in permissions)

    def user_has_role(self, user_id: int, role_slug: str) -> bool:
        """Check if user has specific role"""
        roles = self.get_user_roles(user_id)
        return any(r.slug == role_slug for r in roles)
