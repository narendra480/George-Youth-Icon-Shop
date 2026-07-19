from typing import List, Optional
from sqlalchemy.orm import Session

from app.db.models import Wishlist
from app.repositories.wishlist_repository import WishlistRepository
from app.schemas.wishlist import WishlistResponse


class WishlistService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = WishlistRepository(db)

    def get_wishlist(self, user_id: int) -> List[Wishlist]:
        return self.repo.get_wishlist(user_id)

    def add_item(self, user_id: int, product_id: int, variant_id: Optional[int] = None) -> Wishlist:
        return self.repo.add_item(user_id, product_id, variant_id)

    def remove_item(self, user_id: int, product_id: int, variant_id: Optional[int] = None) -> bool:
        return self.repo.remove_item(user_id, product_id, variant_id)