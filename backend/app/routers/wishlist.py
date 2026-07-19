from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.authorization import require_authentication
from app.db.session import get_db
from app.schemas.wishlist import WishlistCreate, WishlistResponse
from app.services.wishlist_service import WishlistService
from app.db.models import User

router = APIRouter(tags=["Wishlist"])


def get_current_user(auth=Depends(require_authentication)) -> User:
    return auth["user"]


@router.get("/wishlist", response_model=list[WishlistResponse])
def get_wishlist(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    service = WishlistService(db)
    items = service.get_wishlist(user.id)
    return [
        WishlistResponse(
            id=item.id,
            product=item.product,
            variant=item.variant,
            created_at=item.created_at,
        )
        for item in items
    ]


@router.post("/wishlist", response_model=WishlistResponse, status_code=status.HTTP_201_CREATED)
def add_to_wishlist(payload: WishlistCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    service = WishlistService(db)
    item = service.add_item(user.id, payload.product_id, variant_id=payload.variant_id)
    return WishlistResponse(
        id=item.id,
        product=item.product,
        variant=item.variant,
        created_at=item.created_at,
    )


@router.delete("/wishlist/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_from_wishlist(product_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    service = WishlistService(db)
    ok = service.remove_item(user.id, product_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wishlist item not found")