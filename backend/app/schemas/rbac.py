from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel


class RoleResponse(BaseModel):
    id: int
    name: str
    slug: str
    description: Optional[str] = None
    is_system: bool = False
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PermissionResponse(BaseModel):
    id: int
    name: str
    slug: str
    description: Optional[str] = None
    category: str = "general"
    is_system: bool = False
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserRoleResponse(BaseModel):
    id: int
    user_id: int
    role_id: int
    assigned_by: Optional[int] = None
    assigned_at: datetime
    reason: Optional[str] = None

    class Config:
        from_attributes = True