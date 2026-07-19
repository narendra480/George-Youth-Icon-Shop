from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.authorization import require_authentication
from app.db.session import get_db
from app.schemas.cart import CartItemCreate, CartItemResponse, CartResponse
from app.services.cart_service import CartService
from app.db.models import User

router = APIRouter(tags=["Cart"])


def get_current_user(auth=Depends(require_authentication)) -> User:
    return auth["user"]


@router.get("/cart", response_model=CartResponse)
def get_cart(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    service = CartService(db)
    cart = service.get_or_create_cart(user_id=user.id)
    items = service.list_items(cart.id)
    item_responses = []
    for item in items:
        item_responses.append(CartItemResponse(
            id=item.id,
            product=item.product,
            variant=item.variant,
            quantity=item.quantity,
            is_saved_for_later=item.is_saved_for_later,
            created_at=item.created_at,
            updated_at=item.updated_at,
        ))
    return CartResponse(
        id=cart.id,
        user_id=cart.user_id,
        session_id=cart.session_id,
        items=item_responses,
        total_items=len([i for i in items if not i.is_saved_for_later]),
        created_at=cart.created_at,
        updated_at=cart.updated_at,
    )


@router.post("/cart/items", response_model=CartItemResponse, status_code=status.HTTP_201_CREATED)
def add_cart_item(payload: CartItemCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    service = CartService(db)
    cart = service.get_or_create_cart(user_id=user.id)
    item = service.add_item(cart.id, payload.product_id, quantity=payload.quantity, variant_id=payload.variant_id)
    return CartItemResponse(
        id=item.id,
        product=item.product,
        variant=item.variant,
        quantity=item.quantity,
        is_saved_for_later=item.is_saved_for_later,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


@router.put("/cart/items/{item_id}", response_model=CartItemResponse)
def update_cart_item(item_id: int, quantity: int, is_saved_for_later: bool | None = None, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    service = CartService(db)
    item = service.update_quantity(item_id, quantity, is_saved_for_later=is_saved_for_later)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart item not found")
    return CartItemResponse(
        id=item.id,
        product=item.product,
        variant=item.variant,
        quantity=item.quantity,
        is_saved_for_later=item.is_saved_for_later,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


@router.delete("/cart/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_cart_item(item_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    service = CartService(db)
    ok = service.remove_item(item_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart item not found")


@router.post("/cart/clear", status_code=status.HTTP_204_NO_CONTENT)
def clear_cart(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    service = CartService(db)
    cart = service.get_or_create_cart(user_id=user.id)
    service.clear_cart(cart.id)


@router.post("/cart/merge", status_code=status.HTTP_200_OK)
def merge_guest_cart(local_items: list[dict], db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Merge guest cart items into user's cart after login."""
    service = CartService(db)
    cart = service.get_or_create_cart(user_id=user.id)
    merged_count = 0
    for item in local_items:
        try:
            service.add_item(cart.id, product_id=item["product_id"], quantity=item.get("quantity", 1), variant_id=item.get("variant_id"))
            merged_count += 1
        except Exception:
            pass
    return {"merged_items": merged_count, "cart_id": cart.id}


@router.get("/cart/totals")
def cart_totals(coupon_code: str | None = None, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    service = CartService(db)
    cart = service.get_or_create_cart(user_id=user.id)
    items = service.list_items(cart.id)
    cart.items = items
    totals = service.calculate_totals(cart, coupon_code=coupon_code)
    return totals
