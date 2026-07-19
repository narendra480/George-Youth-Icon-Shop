from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class CouponBase(BaseModel):
    code: str
    description: Optional[str] = None
    discount_type: str = Field(..., pattern="^(percentage|fixed)$")
    discount_value: float = Field(..., gt=0)
    min_order_amount: Optional[float] = None
    max_discount_amount: Optional[float] = None
    max_uses: Optional[int] = None
    max_uses_per_user: Optional[int] = None
    is_active: bool = True
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class CouponCreate(CouponBase):
    pass

class CouponUpdate(BaseModel):
    code: Optional[str] = None
    description: Optional[str] = None
    discount_type: Optional[str] = Field(None, pattern="^(percentage|fixed)$")
    discount_value: Optional[float] = Field(None, gt=0)
    min_order_amount: Optional[float] = None
    max_discount_amount: Optional[float] = None
    max_uses: Optional[int] = None
    max_uses_per_user: Optional[int] = None
    is_active: Optional[bool] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class CouponResponse(CouponBase):
    id: int
    used_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CouponValidateResponse(BaseModel):
    valid: bool
    discount_amount: float
    message: str
    coupon: Optional[CouponResponse] = None