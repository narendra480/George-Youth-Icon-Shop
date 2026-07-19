import secrets
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.core.authorization import require_authentication, require_any_permission
from app.db.session import get_db
from app.schemas.order import OrderCreate, OrderUpdate, OrderResponse, OrderStatusHistoryResponse
from app.db.models import Order, OrderItem, OrderStatusHistory, Address, Cart, CartItem, Product, Coupon, Invoice, Shipment, ReturnRequest

router = APIRouter(tags=["Orders"])


def generate_order_number() -> str:
    return f"ORD-{secrets.token_hex(4).upper()}"


def generate_invoice_number() -> str:
    return f"INV-{secrets.token_hex(4).upper()}"


@router.get("/orders", response_model=list[OrderResponse])
def list_orders(db: Session = Depends(get_db), user = Depends(require_authentication)):
    return db.query(Order).filter(Order.user_id == user.id).order_by(Order.created_at.desc()).all()


@router.get("/orders/{order_id}", response_model=OrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db), user = Depends(require_authentication)):
    order = db.query(Order).filter(
        Order.id == order_id, 
        Order.user_id == user.id
    ).options(
        joinedload(Order.items),
        joinedload(Order.address)
    ).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return order


@router.post("/orders", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(payload: OrderCreate, db: Session = Depends(get_db), user = Depends(require_authentication)):
    cart = db.query(Cart).filter(Cart.user_id == user.id).first()
    if not cart or not payload.items:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Empty cart")
    
    cart_items = db.query(CartItem).filter(CartItem.cart_id == cart.id).all()
    if not cart_items:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cart is empty")
    
    subtotal = 0.0
    items_data = []
    for i in payload.items:
        product = db.query(Product).get(i["product_id"])
        if not product:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Product {i['product_id']} not found")
        price = product.offer_price or product.selling_price
        subtotal += price * i["quantity"]
    
    gst_amount = round(subtotal * 0.18, 2)
    shipping_amount = 0.0
    discount_amount = 0.0
    total_amount = subtotal + gst_amount
    
    if payload.coupon_code:
        coupon = db.query(Coupon).filter(Coupon.code == payload.coupon_code, Coupon.is_active == True).first()
        if coupon:
            if coupon.discount_type == "percentage":
                discount_amount = round((subtotal * coupon.discount_value / 100), 2)
            else:
                discount_amount = coupon.discount_value
            total_amount -= discount_amount
    
    address = db.query(Address).filter(Address.id == payload.address_id, Address.user_id == user.id).first()
    if not address:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid address")
    
    order = Order(
        order_number=generate_order_number(),
        user_id=user.id,
        address_id=payload.address_id,
        subtotal=subtotal,
        gst_amount=gst_amount,
        shipping_amount=shipping_amount,
        discount_amount=discount_amount,
        total_amount=total_amount,
        coupon_code=payload.coupon_code,
        status="pending"
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    
    for item in cart_items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=item.product_id,
            variant_id=item.variant_id,
            quantity=item.quantity,
            price=item.product.offer_price or item.product.selling_price,
            mrp=item.product.mrp
        )
        db.add(order_item)
    
    db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
    db.commit()
    
    return db.query(Order).filter(Order.id == order.id).options(
        joinedload(Order.items),
        joinedload(Order.address)
    ).first()


@router.put("/orders/{order_id}", response_model=OrderResponse)
def update_order(order_id: int, payload: OrderUpdate, db: Session = Depends(get_db), user = Depends(require_any_permission("orders.manage", "admin.all"))):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(order, key, value)
    
    if payload.status:
        history = OrderStatusHistory(
            order_id=order.id,
            status=payload.status,
            created_by=user.id
        )
        db.add(history)
    
    db.commit()
    db.refresh(order)
    return order


@router.post("/orders/{order_id}/invoice", response_model=dict)
def generate_invoice(order_id: int, db: Session = Depends(get_db), user = Depends(require_any_permission("orders.manage", "admin.all"))):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    
    invoice = Invoice(
        order_id=order.id,
        invoice_number=generate_invoice_number(),
        invoice_url=f"/invoices/{generate_invoice_number()}.pdf"
    )
    db.add(invoice)
    db.commit()
    db.refresh(invoice)
    
    return {"invoice_id": invoice.id, "invoice_number": invoice.invoice_number, "invoice_url": invoice.invoice_url}


@router.post("/orders/{order_id}/cancel")
def cancel_order(order_id: int, db: Session = Depends(get_db), user = Depends(require_authentication)):
    """Cancel order if not shipped."""
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == user.id
    ).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    if order.status not in ["pending", "confirmed"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot cancel shipped order")
    
    order.status = "cancelled"
    history = OrderStatusHistory(order_id=order.id, status="cancelled", created_by=user.id)
    db.add(history)
    db.commit()
    return {"status": "cancelled"}


@router.post("/orders/{order_id}/return")
def request_return(order_id: int, payload: dict, db: Session = Depends(get_db), user = Depends(require_authentication)):
    """Request return for order."""
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == user.id
    ).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    if order.status != "delivered":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only delivered orders can be returned")
    
    return_req = ReturnRequest(
        order_id=order_id,
        user_id=user.id,
        reason=payload.get("reason"),
        images=payload.get("images"),
        status="pending"
    )
    db.add(return_req)
    db.commit()
    return {"status": "requested", "id": return_req.id}
