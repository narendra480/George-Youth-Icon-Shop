from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class PaymentBase(BaseModel):
    payment_method: str
    amount: float
    currency: str = "INR"


class PaymentCreate(PaymentBase):
    order_id: int
    gateway_order_id: Optional[str] = None


class PaymentUpdate(BaseModel):
    status: Optional[str] = None
    gateway_transaction_id: Optional[str] = None
    gateway_signature: Optional[str] = None


class PaymentResponse(PaymentBase):
    id: int
    order_id: int
    user_id: int
    payment_gateway: Optional[str] = None
    gateway_order_id: Optional[str] = None
    gateway_transaction_id: Optional[str] = None
    gateway_signature: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RazorpayOrderCreate(BaseModel):
    amount: float
    currency: str = "INR"
    receipt: str
    notes: Optional[dict] = None


class RazorpayOrderResponse(BaseModel):
    id: str
    entity: str
    amount: int
    amount_paid: int
    currency: str
    receipt: Optional[str] = None
    status: str
    created_at: int


class PaymentVerification(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str


class TransactionResponse(BaseModel):
    id: int
    payment_id: Optional[int] = None
    order_id: int
    type: str
    amount: float
    balance: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True


class RefundBase(BaseModel):
    payment_id: int
    order_id: int
    amount: float
    reason: Optional[str] = None


class RefundResponse(RefundBase):
    id: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class PaymentAuditResponse(BaseModel):
    id: int
    payment_id: int
    action: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True