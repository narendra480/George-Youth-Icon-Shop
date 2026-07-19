import hashlib
import hmac
import os
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from datetime import datetime
import httpx

from app.core.authorization import require_authentication
from app.db.session import get_db
from app.db.models import User, Order, Payment, PaymentAudit
from app.schemas.payment import (
    PaymentCreate, PaymentResponse, PaymentVerification, RazorpayOrderResponse,
    RazorpayOrderCreate
)

router = APIRouter(tags=["Payments"])

RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID", "")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET", "")
RAZORPAY_API_URL = "https://api.razorpay.com/v1"


def get_current_user(auth=Depends(require_authentication)) -> User:
    return auth["user"]


def verify_razorpay_signature(order_id: str, payment_id: str, signature: str) -> bool:
    message = f"{order_id}|{payment_id}"
    expected_signature = hmac.new(
        RAZORPAY_KEY_SECRET.encode(),
        message.encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected_signature, signature)


async def create_razorpay_order(amount: float, receipt: str, notes: dict = None) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{RAZORPAY_API_URL}/orders",
            auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET),
            json={
                "amount": int(amount * 100),
                "currency": "INR",
                "receipt": receipt,
                "notes": notes or {}
            }
        )
        response.raise_for_status()
        return response.json()


async def verify_razorpay_payment(payment_id: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{RAZORPAY_API_URL}/payments/{payment_id}",
            auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET)
        )
        response.raise_for_status()
        return response.json()


@router.post("/payments/create-order", response_model=RazorpayOrderResponse)
async def create_payment_order(
    payload: RazorpayOrderCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Create a Razorpay order for payment."""
    return await create_razorpay_order(payload.amount, payload.receipt, payload.notes)


@router.post("/payments/verify", response_model=PaymentResponse)
async def verify_payment(
    payload: PaymentVerification,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Verify Razorpay payment signature and update order."""
    if not verify_razorpay_signature(
        payload.razorpay_order_id,
        payload.razorpay_payment_id,
        payload.razorpay_signature
    ):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid signature")
    
    payment_data = await verify_razorpay_payment(payload.razorpay_payment_id)
    
    order = db.query(Order).filter(Order.id == int(payload.razorpay_order_id)).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    
    payment = Payment(
        order_id=order.id,
        user_id=user.id,
        payment_method="razorpay",
        payment_gateway="razorpay",
        gateway_order_id=payload.razorpay_order_id,
        gateway_transaction_id=payload.razorpay_payment_id,
        amount=order.total_amount,
        currency="INR",
        status="completed"
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)
    
    order.payment_status = "paid"
    order.payment_method = "razorpay"
    db.commit()
    
    audit = PaymentAudit(
        payment_id=payment.id,
        action="payment_verified",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent")
    )
    db.add(audit)
    db.commit()
    
    return PaymentResponse(
        id=payment.id,
        order_id=payment.order_id,
        user_id=payment.user_id,
        payment_method=payment.payment_method,
        amount=payment.amount,
        currency=payment.currency,
        payment_gateway=payment.payment_gateway,
        gateway_order_id=payment.gateway_order_id,
        gateway_transaction_id=payment.gateway_transaction_id,
        status=payment.status,
        created_at=payment.created_at,
        updated_at=payment.updated_at
    )


@router.post("/payments/webhook")
async def payment_webhook(request: Request, db: Session = Depends(get_db)):
    """Handle Razorpay webhooks for payment events."""
    payload = await request.body()
    signature = request.headers.get("x-razorpay-signature", "")
    
    expected_signature = hmac.new(
        RAZORPAY_KEY_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    if not hmac.compare_digest(expected_signature, signature):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid webhook signature")
    
    data = await request.json()
    event = data.get("event")
    
    if event == "payment.captured":
        payment_id = data["payload"]["payment"]["entity"]["id"]
        # Update payment status - implemented in production
    elif event == "payment.failed":
        payment_id = data["payload"]["payment"]["entity"]["id"]
        # Handle failed payment - implemented in production
    elif event in ["refund.created", "refund.processed"]:
        payment_id = data["payload"]["refund"]["entity"]["id"]
        # Handle refund - implemented in production
    elif event == "payment.dispute.created":
        payment_id = data["payload"]["payment"]["entity"]["id"]
        # Handle chargeback - implemented in production
    return {"status": "ok"}


@router.get("/payments/history")
async def payment_history(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Get payment history for user."""
    payments = db.query(Payment).filter(
        Payment.user_id == user.id
    ).order_by(Payment.created_at.desc()).all()
    
    return [
        PaymentResponse(
            id=p.id,
            order_id=p.order_id,
            user_id=p.user_id,
            payment_method=p.payment_method,
            amount=p.amount,
            currency=p.currency,
            payment_gateway=p.payment_gateway,
            gateway_order_id=p.gateway_order_id,
            gateway_transaction_id=p.gateway_transaction_id,
            status=p.status,
            created_at=p.created_at,
            updated_at=p.updated_at
        )
        for p in payments
    ]