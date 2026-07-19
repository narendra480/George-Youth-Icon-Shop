from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel


class CategoryBase(BaseModel):
    name: str
    slug: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[int] = None
    banner_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    icon_url: Optional[str] = None
    is_featured: bool = False
    display_order: int = 0
    is_active: bool = True


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[int] = None
    banner_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    icon_url: Optional[str] = None
    is_featured: Optional[bool] = None
    display_order: Optional[int] = None
    is_active: Optional[bool] = None


class CategoryResponse(CategoryBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True