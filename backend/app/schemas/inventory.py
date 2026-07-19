from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class InventoryBase(BaseModel):
    product_id: Optional[int] = None
    variant_id: Optional[int] = None
    current_stock: int = Field(0, ge=0)
    reserved_stock: int = Field(0, ge=0)
    reorder_level: int = Field(0, ge=0)
    low_stock_alert: bool = False


class InventoryCreate(InventoryBase):
    pass


class InventoryUpdate(BaseModel):
    current_stock: Optional[int] = Field(None, ge=0)
    reserved_stock: Optional[int] = Field(None, ge=0)
    reorder_level: Optional[int] = Field(None, ge=0)
    low_stock_alert: Optional[bool] = None


class InventoryHistoryResponse(BaseModel):
    id: int
    product_id: int
    variant_id: Optional[int] = None
    change_type: str
    quantity_change: int
    previous_stock: int
    new_stock: int
    reference_id: Optional[str] = None
    notes: Optional[str] = None
    created_by: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class InventoryResponse(BaseModel):
    id: int
    product_id: int
    variant_id: Optional[int] = None
    current_stock: int
    reserved_stock: int
    available_stock: int
    reorder_level: int
    low_stock_alert: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
