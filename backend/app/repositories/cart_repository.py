from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.models import Cart, CartItem, Product, ProductVariant
from app.schemas.cart import CartItemCreate


class CartRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_cart(self, user_id: Optional[int] = None, session_id: Optional[str] = None) -> Optional[Cart]:
        return (
            self.session.query(Cart)
            .filter(
                (Cart.user_id == user_id) if user_id else (Cart.session_id == session_id)
            )
            .first()
        )

    def get_or_create_cart(self, user_id: Optional[int] = None, session_id: Optional[str] = None) -> Cart:
        cart = self.get_cart(user_id=user_id, session_id=session_id)
        if not cart:
            cart = Cart(user_id=user_id, session_id=session_id)
            self.session.add(cart)
            self.session.commit()
            self.session.refresh(cart)
        return cart

    def list_items(self, cart_id: int, include_saved: bool = True) -> List[CartItem]:
        query = self.session.query(CartItem).filter(CartItem.cart_id == cart_id)
        if not include_saved:
            query = query.filter(CartItem.is_saved_for_later == False)
        return query.all()

    def add_item(self, cart_id: int, payload: CartItemCreate) -> CartItem:
        existing = (
            self.session.query(CartItem)
            .filter(
                CartItem.cart_id == cart_id,
                CartItem.product_id == payload.product_id,
                CartItem.variant_id == payload.variant_id,
                CartItem.is_saved_for_later == False,
            )
            .first()
        )
        if existing:
            existing.quantity += payload.quantity
            self.session.commit()
            self.session.refresh(existing)
            return existing
        item = CartItem(**payload.model_dump(), cart_id=cart_id)
        self.session.add(item)
        self.session.commit()
        self.session.refresh(item)
        return item

    def update_item(self, item_id: int, quantity: int, is_saved_for_later: Optional[bool] = None) -> Optional[CartItem]:
        item = self.session.query(CartItem).filter(CartItem.id == item_id).first()
        if not item:
            return None
        item.quantity = quantity
        if is_saved_for_later is not None:
            item.is_saved_for_later = is_saved_for_later
        self.session.commit()
        self.session.refresh(item)
        return item

    def remove_item(self, item_id: int) -> bool:
        item = self.session.query(CartItem).filter(CartItem.id == item_id).first()
        if not item:
            return False
        self.session.delete(item)
        self.session.commit()
        return True

    def clear_cart(self, cart_id: int) -> None:
        self.session.query(CartItem).filter(CartItem.cart_id == cart_id, CartItem.is_saved_for_later == False).delete()
        self.session.commit()