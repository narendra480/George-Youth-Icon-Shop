from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from app.db.models import Cart, CartItem, Product, ProductVariant, Coupon, CouponUsage
from app.repositories.cart_repository import CartRepository
from app.schemas.cart import CartItemCreate, CartItemResponse, CartResponse


class CartService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = CartRepository(db)

    def get_or_create_cart(self, user_id: Optional[int] = None, session_id: Optional[str] = None) -> Cart:
        return self.repo.get_or_create_cart(user_id=user_id, session_id=session_id)

    def list_items(self, cart_id: int, include_saved: bool = True) -> List[CartItem]:
        return self.repo.list_items(cart_id, include_saved=include_saved)

    def add_item(self, cart_id: int, product_id: int, quantity: int = 1, variant_id: Optional[int] = None) -> CartItem:
        item = self.repo.add_item(cart_id, CartItemCreate(product_id=product_id, variant_id=variant_id, quantity=quantity))
        return item

    def update_quantity(self, item_id: int, quantity: int, is_saved_for_later: Optional[bool] = None) -> Optional[CartItem]:
        return self.repo.update_item(item_id, quantity, is_saved_for_later=is_saved_for_later)

    def remove_item(self, item_id: int) -> bool:
        return self.repo.remove_item(item_id)

    def clear_cart(self, cart_id: int) -> None:
        self.repo.clear_cart(cart_id)

    def calculate_totals(self, cart: Cart, coupon_code: Optional[str] = None) -> dict:
        active_items = [item for item in cart.items if not item.is_saved_for_later]
        subtotal = 0.0
        for item in active_items:
            price = item.product.selling_price
            subtotal += price * item.quantity
        subtotal = round(subtotal, 2)
        discount = 0.0
        coupon = None
        if coupon_code:
            coupon = self.db.query(Coupon).filter(Coupon.code == coupon_code, Coupon.is_active == True).first()
            if coupon:
                now = datetime.utcnow()
                valid = True
                message = "Valid coupon"
                if coupon.start_date and now < coupon.start_date:
                    valid = False
                    message = "Coupon not started yet"
                if coupon.end_date and now > coupon.end_date:
                    valid = False
                    message = "Coupon expired"
                if coupon.min_order_amount and subtotal < coupon.min_order_amount:
                    valid = False
                    message = f"Minimum order amount {coupon.min_order_amount} required"
                if coupon.max_uses and coupon.used_count >= coupon.max_uses:
                    valid = False
                    message = "Coupon usage limit exceeded"
                if valid:
                    if coupon.discount_type == "percentage":
                        discount = subtotal * (coupon.discount_value / 100)
                    else:
                        discount = coupon.discount_value
                    if coupon.max_discount_amount:
                        discount = min(discount, coupon.max_discount_amount)
                    discount = round(discount, 2)
        gst = round(subtotal * 0.18, 2)  # Assuming 18% GST; in real app use product-level GST
        shipping = 0.0 if subtotal >= 1000 else 50.0
        grand_total = round(subtotal - discount + shipping, 2)
        return {
            "subtotal": subtotal,
            "discount": discount,
            "gst": gst,
            "shipping": shipping,
            "grand_total": grand_total,
            "coupon": coupon,
            "message": message if coupon_code else "",
        }