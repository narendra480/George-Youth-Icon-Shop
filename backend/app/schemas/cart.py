from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from app.schemas.product import ProductResponse


class CartItemBase(BaseModel):
    product_id: int
    variant_id: Optional[int] = None
    quantity: int = Field(1, ge=1)
    is_saved_for_later: bool = False


class CartItemCreate(CartItemBase):
    pass


class CartItemResponse(BaseModel):
    id: int
    product: ProductResponse
    variant: Optional[dict] = None
    quantity: int
    is_saved_for_later: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CartResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    session_id: Optional[str] = None
    items: list[CartItemResponse] = []
    total_items: int = 0
    subtotal: float = 0.0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True