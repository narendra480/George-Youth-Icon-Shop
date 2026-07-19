from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class OrderItemBase(BaseModel):
    product_id: int
    variant_id: Optional[int] = None
    quantity: int
    price: float
    mrp: float


class OrderItemResponse(OrderItemBase):
    id: int
    order_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class AddressResponse(BaseModel):
    id: int
    name: str
    mobile: str
    house_flat: str
    street: str
    city: str
    state: str
    pincode: str

    class Config:
        from_attributes = True


class OrderBase(BaseModel):
    address_id: int
    coupon_code: Optional[str] = None
    payment_method: Optional[str] = None


class OrderCreate(BaseModel):
    address_id: int
    items: List[dict]
    coupon_code: Optional[str] = None


class OrderUpdate(BaseModel):
    status: Optional[str] = None
    payment_status: Optional[str] = None
    payment_method: Optional[str] = None
    delivery_estimate: Optional[str] = None


class OrderResponse(OrderBase):
    id: int
    order_number: str
    user_id: int
    subtotal: float
    gst_amount: float
    shipping_amount: float
    discount_amount: float
    total_amount: float
    status: str
    payment_status: str
    payment_method: Optional[str] = None
    delivery_estimate: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    items: Optional[List[OrderItemResponse]] = None
    address: Optional[AddressResponse] = None

    class Config:
        from_attributes = True


class OrderStatusHistoryBase(BaseModel):
    status: str
    note: Optional[str] = None


class OrderStatusHistoryResponse(OrderStatusHistoryBase):
    id: int
    order_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class InvoiceResponse(BaseModel):
    id: int
    order_id: int
    invoice_number: str
    invoice_url: Optional[str] = None

    class Config:
        from_attributes = True