from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class ReviewUserResponse(BaseModel):
    id: int
    first_name: Optional[str] = None
    last_name: Optional[str] = None

    class Config:
        from_attributes = True

class ReviewBase(BaseModel):
    product_id: int
    rating: int = Field(..., ge=1, le=5)
    title: Optional[str] = None
    comment: Optional[str] = None

class ReviewCreate(ReviewBase):
    pass

class ReviewUpdate(BaseModel):
    rating: Optional[int] = Field(None, ge=1, le=5)
    title: Optional[str] = None
    comment: Optional[str] = None

class ReviewResponse(ReviewBase):
    id: int
    user_id: int
    is_verified_purchase: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime
    user: Optional[ReviewUserResponse] = None

    class Config:
        from_attributes = True
