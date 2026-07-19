from typing import List, Optional
from sqlalchemy.orm import Session

from app.db.models import Wishlist


class WishlistRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_wishlist(self, user_id: int) -> List[Wishlist]:
        return self.session.query(Wishlist).filter(Wishlist.user_id == user_id).all()

    def add_item(self, user_id: int, product_id: int, variant_id: Optional[int] = None) -> Wishlist:
        existing = self.session.query(Wishlist).filter(
            Wishlist.user_id == user_id,
            Wishlist.product_id == product_id,
            Wishlist.variant_id == variant_id,
        ).first()
        if existing:
            return existing
        item = Wishlist(user_id=user_id, product_id=product_id, variant_id=variant_id)
        self.session.add(item)
        self.session.commit()
        self.session.refresh(item)
        return item

    def remove_item(self, user_id: int, product_id: int, variant_id: Optional[int] = None) -> bool:
        item = self.session.query(Wishlist).filter(
            Wishlist.user_id == user_id,
            Wishlist.product_id == product_id,
            Wishlist.variant_id == variant_id,
        ).first()
        if not item:
            return False
        self.session.delete(item)
        self.session.commit()
        return True