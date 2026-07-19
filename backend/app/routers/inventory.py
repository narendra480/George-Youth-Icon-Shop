from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.authorization import require_authentication, require_any_permission
from app.db.models import Product
from app.db.session import get_db
from app.schemas.inventory import (
    InventoryCreate,
    InventoryResponse,
    InventoryUpdate,
    InventoryHistoryResponse,
)
from app.services.inventory_service import InventoryService
from sqlalchemy.orm import Session

router = APIRouter(tags=["Inventory"])


def _to_response(inventory) -> dict:
    data = InventoryResponse.from_orm(inventory).dict()
    data["available_stock"] = max(0, inventory.current_stock - inventory.reserved_stock)
    return data


@router.get("/inventory")
def list_inventory(
    product_id: int | None = None,
    variant_id: int | None = None,
    low_stock_only: bool = False,
    db: Session = Depends(get_db),
) -> list[dict]:
    service = InventoryService(db)
    items = service.list_inventories(product_id=product_id, variant_id=variant_id, low_stock_only=low_stock_only)
    return [_to_response(i) for i in items]


@router.get("/inventory/low-stock")
def low_stock_alert(db: Session = Depends(get_db)) -> list[dict]:
    service = InventoryService(db)
    items = service.list_inventories(low_stock_only=True)
    return [_to_response(i) for i in items]


@router.post("/inventory", response_model=InventoryResponse, status_code=status.HTTP_201_CREATED)
def create_or_update_inventory(
    payload: InventoryCreate,
    db: Session = Depends(get_db),
    auth=Depends(require_any_permission("inventory.manage", "products.manage", "admin.all")),
):
    service = InventoryService(db)
    inventory = service.create_or_update_inventory(
        product_id=payload.product_id,
        variant_id=payload.variant_id,
        current_stock=payload.current_stock,
        reserved_stock=payload.reserved_stock,
        reorder_level=payload.reorder_level,
        low_stock_alert=payload.low_stock_alert,
    )
    return _to_response(inventory)


@router.put("/inventory/{inventory_id}", response_model=InventoryResponse)
def update_inventory(
    inventory_id: int,
    payload: InventoryUpdate,
    db: Session = Depends(get_db),
    auth=Depends(require_any_permission("inventory.manage", "products.manage", "admin.all")),
):
    service = InventoryService(db)
    existing = service.get_inventory(payload.product_id or 0, payload.variant_id)
    if not existing or existing.id != inventory_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inventory not found")
    updated = service.create_or_update_inventory(
        product_id=existing.product_id,
        variant_id=existing.variant_id,
        current_stock=payload.current_stock if payload.current_stock is not None else existing.current_stock,
        reserved_stock=payload.reserved_stock if payload.reserved_stock is not None else existing.reserved_stock,
        reorder_level=payload.reorder_level if payload.reorder_level is not None else existing.reorder_level,
        low_stock_alert=payload.low_stock_alert if payload.low_stock_alert is not None else existing.low_stock_alert,
    )
    return _to_response(updated)


@router.post("/inventory/stock-in")
def stock_in(
    product_id: int,
    quantity: int,
    variant_id: int | None = None,
    created_by: int | None = None,
    reference_id: str | None = None,
    notes: str | None = None,
    db: Session = Depends(get_db),
    auth=Depends(require_any_permission("inventory.manage", "products.manage", "admin.all")),
):
    service = InventoryService(db)
    product = db.query(Product).filter(Product.id == product_id, Product.deleted_at.is_(None)).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    inv = service.stock_in(product_id, quantity, variant_id=variant_id, created_by=created_by or auth["user"].id, reference_id=reference_id, notes=notes)
    return _to_response(inv)


@router.post("/inventory/stock-out")
def stock_out(
    product_id: int,
    quantity: int,
    variant_id: int | None = None,
    created_by: int | None = None,
    reference_id: str | None = None,
    notes: str | None = None,
    db: Session = Depends(get_db),
    auth=Depends(require_any_permission("inventory.manage", "products.manage", "admin.all")),
):
    service = InventoryService(db)
    product = db.query(Product).filter(Product.id == product_id, Product.deleted_at.is_(None)).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    inv = service.stock_out(product_id, quantity, variant_id=variant_id, created_by=created_by or auth["user"].id, reference_id=reference_id, notes=notes)
    return _to_response(inv)


@router.post("/inventory/adjustment")
def stock_adjustment(
    product_id: int,
    new_stock: int,
    variant_id: int | None = None,
    created_by: int | None = None,
    notes: str | None = None,
    db: Session = Depends(get_db),
    auth=Depends(require_any_permission("inventory.manage", "products.manage", "admin.all")),
):
    service = InventoryService(db)
    product = db.query(Product).filter(Product.id == product_id, Product.deleted_at.is_(None)).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    inv = service.adjust_stock(product_id, new_stock, variant_id=variant_id, created_by=created_by or auth["user"].id, notes=notes)
    return _to_response(inv)


@router.get("/inventory/history", response_model=list[InventoryHistoryResponse])
def get_inventory_history(
    product_id: int | None = None,
    variant_id: int | None = None,
    change_type: str | None = None,
    limit: int = 100,
    db: Session = Depends(get_db),
) -> list[InventoryHistoryResponse]:
    service = InventoryService(db)
    items = service.get_history(product_id=product_id, variant_id=variant_id, change_type=change_type, limit=limit)
    return [InventoryHistoryResponse.from_orm(i).dict() for i in items]