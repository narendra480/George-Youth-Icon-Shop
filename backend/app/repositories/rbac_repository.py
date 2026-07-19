import logging
from typing import List, Optional
from sqlalchemy.orm import Session

from app.db.models import Permission, Role, UserRole, User

logger = logging.getLogger("app.rbac_repository")


class RoleRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, name: str, slug: str, description: Optional[str] = None, is_system: bool = False) -> Role:
        role = Role(name=name, slug=slug, description=description, is_system=is_system)
        self.db.add(role)
        self.db.commit()
        self.db.refresh(role)
        logger.info(f"RBAC | ROLE_CREATED | Role: {name} (id: {role.id})")
        return role

    def get_by_id(self, role_id: int) -> Optional[Role]:
        return self.db.query(Role).filter(Role.id == role_id).first()

    def get_by_slug(self, slug: str) -> Optional[Role]:
        return self.db.query(Role).filter(Role.slug == slug).first()

    def get_by_name(self, name: str) -> Optional[Role]:
        return self.db.query(Role).filter(Role.name == name).first()

    def list_all(self) -> List[Role]:
        return self.db.query(Role).all()

    def update(self, role_id: int, name: Optional[str] = None, slug: Optional[str] = None, description: Optional[str] = None) -> Optional[Role]:
        role = self.get_by_id(role_id)
        if not role:
            return None
        
        if name:
            role.name = name
        if slug:
            role.slug = slug
        if description is not None:
            role.description = description

        self.db.commit()
        self.db.refresh(role)
        logger.info(f"RBAC | ROLE_UPDATED | Role id: {role_id}")
        return role

    def delete(self, role_id: int) -> bool:
        role = self.get_by_id(role_id)
        if not role:
            return False
        
        if role.is_system:
            logger.warning(f"RBAC | ROLE_DELETE_DENIED | Cannot delete system role: {role.name}")
            raise ValueError("Cannot delete system roles")

        self.db.delete(role)
        self.db.commit()
        logger.info(f"RBAC | ROLE_DELETED | Role id: {role_id}")
        return True

    def assign_permission(self, role_id: int, permission_id: int) -> bool:
        role = self.get_by_id(role_id)
        permission = self.db.query(Permission).filter(Permission.id == permission_id).first()
        
        if not role or not permission:
            return False

        if permission not in role.permissions:
            role.permissions.append(permission)
            self.db.commit()
            logger.info(f"RBAC | PERMISSION_ASSIGNED | Role: {role.name}, Permission: {permission.name}")
            return True

        return True

    def remove_permission(self, role_id: int, permission_id: int) -> bool:
        role = self.get_by_id(role_id)
        permission = self.db.query(Permission).filter(Permission.id == permission_id).first()
        
        if not role or not permission:
            return False

        if permission in role.permissions:
            role.permissions.remove(permission)
            self.db.commit()
            logger.info(f"RBAC | PERMISSION_REMOVED | Role: {role.name}, Permission: {permission.name}")
            return True

        return True

    def get_permissions(self, role_id: int) -> List[Permission]:
        role = self.get_by_id(role_id)
        return role.permissions if role else []


class PermissionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, name: str, slug: str, description: Optional[str] = None, category: str = "general", is_system: bool = False) -> Permission:
        permission = Permission(name=name, slug=slug, description=description, category=category, is_system=is_system)
        self.db.add(permission)
        self.db.commit()
        self.db.refresh(permission)
        logger.info(f"RBAC | PERMISSION_CREATED | Permission: {name} (id: {permission.id})")
        return permission

    def get_by_id(self, permission_id: int) -> Optional[Permission]:
        return self.db.query(Permission).filter(Permission.id == permission_id).first()

    def get_by_slug(self, slug: str) -> Optional[Permission]:
        return self.db.query(Permission).filter(Permission.slug == slug).first()

    def get_by_name(self, name: str) -> Optional[Permission]:
        return self.db.query(Permission).filter(Permission.name == name).first()

    def list_all(self) -> List[Permission]:
        return self.db.query(Permission).all()

    def list_by_category(self, category: str) -> List[Permission]:
        return self.db.query(Permission).filter(Permission.category == category).all()

    def update(self, permission_id: int, name: Optional[str] = None, slug: Optional[str] = None, description: Optional[str] = None, category: Optional[str] = None) -> Optional[Permission]:
        permission = self.get_by_id(permission_id)
        if not permission:
            return None

        if name:
            permission.name = name
        if slug:
            permission.slug = slug
        if description is not None:
            permission.description = description
        if category:
            permission.category = category

        self.db.commit()
        self.db.refresh(permission)
        logger.info(f"RBAC | PERMISSION_UPDATED | Permission id: {permission_id}")
        return permission

    def delete(self, permission_id: int) -> bool:
        permission = self.get_by_id(permission_id)
        if not permission:
            return False

        if permission.is_system:
            logger.warning(f"RBAC | PERMISSION_DELETE_DENIED | Cannot delete system permission: {permission.name}")
            raise ValueError("Cannot delete system permissions")

        self.db.delete(permission)
        self.db.commit()
        logger.info(f"RBAC | PERMISSION_DELETED | Permission id: {permission_id}")
        return True


class UserRoleRepository:
    def __init__(self, db: Session):
        self.db = db

    def assign_role(self, user_id: int, role_id: int, assigned_by: Optional[int] = None, reason: Optional[str] = None) -> UserRole:
        # Check if already assigned
        existing = self.db.query(UserRole).filter(
            UserRole.user_id == user_id,
            UserRole.role_id == role_id
        ).first()

        if existing:
            logger.info(f"RBAC | ROLE_ALREADY_ASSIGNED | User: {user_id}, Role: {role_id}")
            return existing

        user_role = UserRole(user_id=user_id, role_id=role_id, assigned_by=assigned_by, reason=reason)
        self.db.add(user_role)
        self.db.commit()
        self.db.refresh(user_role)
        logger.info(f"RBAC | ROLE_ASSIGNED | User: {user_id}, Role: {role_id}, Assigned by: {assigned_by}")
        return user_role

    def remove_role(self, user_id: int, role_id: int) -> bool:
        user_role = self.db.query(UserRole).filter(
            UserRole.user_id == user_id,
            UserRole.role_id == role_id
        ).first()

        if not user_role:
            return False

        self.db.delete(user_role)
        self.db.commit()
        logger.info(f"RBAC | ROLE_REMOVED | User: {user_id}, Role: {role_id}")
        return True

    def get_user_roles(self, user_id: int) -> List[UserRole]:
        return self.db.query(UserRole).filter(UserRole.user_id == user_id).all()

    def get_role_users(self, role_id: int) -> List[UserRole]:
        return self.db.query(UserRole).filter(UserRole.role_id == role_id).all()

    def get_by_id(self, user_role_id: int) -> Optional[UserRole]:
        return self.db.query(UserRole).filter(UserRole.id == user_role_id).first()
