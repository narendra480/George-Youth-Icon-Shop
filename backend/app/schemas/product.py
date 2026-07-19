from datetime import datetime
from typing import Any, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class ProductBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=255)
    slug: Optional[str] = Field(None, min_length=3, max_length=255)
    sku: Optional[str] = Field(None, min_length=3, max_length=64)
    barcode: Optional[str] = Field(None, max_length=64)
    short_description: Optional[str] = Field(None, max_length=512)
    description: Optional[str] = None
    specifications: Optional[dict[str, Any]] = None
    search_keywords: Optional[str] = Field(None, max_length=512)
    tags: Optional[list[str]] = None
    dimensions: Optional[dict[str, Any]] = None
    weight: Optional[float] = Field(None, ge=0)
    weight_unit: Optional[str] = Field("kg", max_length=16)
    gst_percentage: Optional[float] = Field(None, ge=0, le=100)
    hsn_code: Optional[str] = Field(None, max_length=16)
    country_of_origin: Optional[str] = Field(None, max_length=64)
    manufacturer: Optional[str] = Field(None, max_length=255)

    cost_price: Optional[float] = Field(None, ge=0)
    mrp: float = Field(..., gt=0)
    selling_price: float = Field(..., gt=0)
    discount_percentage: float = Field(0.0, ge=0, le=100)
    offer_price: Optional[float] = Field(None, gt=0)
    offer_start_date: Optional[datetime] = None
    offer_end_date: Optional[datetime] = None

    is_featured: bool = False
    is_new_arrival: bool = False
    is_best_seller: bool = False
    status: str = Field("draft", pattern="^(draft|active|out_of_stock|archived)$")

    category_id: int
    brand_id: Optional[int] = None


class ProductCreate(ProductBase):
    images: Optional[list[str]] = None
    primary_image_index: Optional[int] = 0


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=255)
    slug: Optional[str] = Field(None, min_length=3, max_length=255)
    sku: Optional[str] = Field(None, min_length=3, max_length=64)
    barcode: Optional[str] = Field(None, max_length=64)
    short_description: Optional[str] = Field(None, max_length=512)
    description: Optional[str] = None
    specifications: Optional[dict[str, Any]] = None
    search_keywords: Optional[str] = Field(None, max_length=512)
    tags: Optional[list[str]] = None
    dimensions: Optional[dict[str, Any]] = None
    weight: Optional[float] = Field(None, ge=0)
    weight_unit: Optional[str] = Field(None, max_length=16)
    gst_percentage: Optional[float] = Field(None, ge=0, le=100)
    hsn_code: Optional[str] = Field(None, max_length=16)
    country_of_origin: Optional[str] = Field(None, max_length=64)
    manufacturer: Optional[str] = Field(None, max_length=255)

    cost_price: Optional[float] = Field(None, ge=0)
    mrp: Optional[float] = Field(None, gt=0)
    selling_price: Optional[float] = Field(None, gt=0)
    discount_percentage: Optional[float] = Field(None, ge=0, le=100)
    offer_price: Optional[float] = Field(None, gt=0)
    offer_start_date: Optional[datetime] = None
    offer_end_date: Optional[datetime] = None

    is_featured: Optional[bool] = None
    is_new_arrival: Optional[bool] = None
    is_best_seller: Optional[bool] = None
    status: Optional[str] = Field(None, pattern="^(draft|active|out_of_stock|archived)$")

    category_id: Optional[int] = None
    brand_id: Optional[int] = None


class ProductImageResponse(BaseModel):
    id: int
    image_path: str
    alt_text: Optional[str] = None
    sort_order: int = 0
    is_primary: bool = False
    created_at: datetime

    class Config:
        from_attributes = True


class ProductVariantResponse(BaseModel):
    id: int
    sku: str
    name: Optional[str] = None
    attributes: Optional[dict[str, Any]] = None
    images: Optional[list[str]] = None
    price: Optional[float] = None
    mrp: Optional[float] = None
    inventory_quantity: int = 0
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProductResponse(BaseModel):
    id: int
    name: str
    slug: str
    sku: Optional[str] = None
    barcode: Optional[str] = None
    short_description: Optional[str] = None
    description: Optional[str] = None
    specifications: Optional[dict[str, Any]] = None
    search_keywords: Optional[str] = None
    tags: Optional[list[str]] = None
    dimensions: Optional[dict[str, Any]] = None
    weight: Optional[float] = None
    weight_unit: Optional[str] = "kg"
    gst_percentage: Optional[float] = None
    hsn_code: Optional[str] = None
    country_of_origin: Optional[str] = None
    manufacturer: Optional[str] = None

    cost_price: Optional[float] = None
    mrp: float
    selling_price: float
    discount_percentage: float = 0.0
    offer_price: Optional[float] = None
    offer_start_date: Optional[datetime] = None
    offer_end_date: Optional[datetime] = None

    you_save: Optional[float] = None

    is_featured: bool = False
    is_new_arrival: bool = False
    is_best_seller: bool = False
    status: str

    category_id: int
    brand_id: Optional[int] = None

    images: list[ProductImageResponse] = []
    variants: list[ProductVariantResponse] = []

    category: Optional[Any] = None
    brand: Optional[Any] = None

    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True


def compute_offer_snapshot(payload: ProductBase | ProductUpdate | ProductResponse) -> dict[str, Any]:
    mrp = getattr(payload, "mrp", None)
    selling_price = getattr(payload, "selling_price", None)
    offer_price = getattr(payload, "offer_price", None)
    discount = getattr(payload, "discount_percentage", 0.0) or 0.0

    base_price = offer_price if offer_price is not None else selling_price
    you_save = None
    discount_pct = discount

    if mrp is not None and base_price is not None:
        you_save = max(0.0, mrp - base_price)
        if discount_pct == 0.0 and mrp > 0:
            discount_pct = round((you_save / mrp) * 100, 2)

    effective_offer_price = base_price
    if effective_offer_price is not None:
        effective_offer_price = round(effective_offer_price, 2)

    return {
        "you_save": round(you_save, 2) if you_save is not None else None,
        "discount_percentage": discount_pct,
        "effective_offer_price": effective_offer_price,
    }