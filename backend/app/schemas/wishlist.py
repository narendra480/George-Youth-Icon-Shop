from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from app.schemas.product import ProductResponse


class WishlistCreate(BaseModel):
    product_id: int
    variant_id: Optional[int] = None


class WishlistResponse(BaseModel):
    id: int
    product: ProductResponse
    variant: Optional[dict] = None
    created_at: datetime

    class Config:
        from_attributes = True
