from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from app.db.models import Inventory, InventoryHistory, Product, ProductVariant


class InventoryRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_inventory(self, product_id: int, variant_id: Optional[int] = None) -> Optional[Inventory]:
        return (
            self.session.query(Inventory)
            .filter(Inventory.product_id == product_id, Inventory.variant_id == variant_id)
            .first()
        )

    def list_inventories(self, product_id: Optional[int] = None, variant_id: Optional[int] = None, low_stock_only: bool = False) -> List[Inventory]:
        query = self.session.query(Inventory)
        if product_id is not None:
            query = query.filter(Inventory.product_id == product_id)
        if variant_id is not None:
            query = query.filter(Inventory.variant_id == variant_id)
        if low_stock_only:
            query = query.filter(Inventory.low_stock_alert.is_(True))
        return query.all()

    def create_or_update(self, product_id: int, variant_id: Optional[int], current_stock: int, reserved_stock: int = 0, reorder_level: int = 0, low_stock_alert: bool = False) -> Inventory:
        inventory = self.get_inventory(product_id, variant_id)
        if inventory:
            inventory.current_stock = current_stock
            inventory.reserved_stock = reserved_stock
            inventory.reorder_level = reorder_level
            inventory.low_stock_alert = low_stock_alert
            inventory.updated_at = datetime.utcnow()
        else:
            inventory = Inventory(
                product_id=product_id,
                variant_id=variant_id,
                current_stock=current_stock,
                reserved_stock=reserved_stock,
                reorder_level=reorder_level,
                low_stock_alert=low_stock_alert,
            )
            self.session.add(inventory)
        self.session.commit()
        self.session.refresh(inventory)
        return inventory

    def adjust_stock(self, product_id: int, variant_id: Optional[int], change: int, change_type: str, created_by: Optional[int] = None, reference_id: Optional[str] = None, notes: Optional[str] = None) -> Optional[Inventory]:
        inventory = self.get_inventory(product_id, variant_id)
        if not inventory:
            inventory = self.create_or_update(product_id, variant_id, current_stock=max(0, change), reserved_stock=0)
            previous = 0
            new = inventory.current_stock
        else:
            previous = inventory.current_stock
            new = max(0, previous + change)
            inventory.current_stock = new
            inventory.low_stock_alert = new <= inventory.reorder_level
            inventory.updated_at = datetime.utcnow()
            self.session.commit()
            self.session.refresh(inventory)

        history = InventoryHistory(
            product_id=product_id,
            variant_id=variant_id,
            change_type=change_type,
            quantity_change=change,
            previous_stock=previous,
            new_stock=new,
            reference_id=reference_id,
            notes=notes,
            created_by=created_by,
        )
        self.session.add(history)
        self.session.commit()
        return inventory

    def get_history(self, product_id: Optional[int] = None, variant_id: Optional[int] = None, change_type: Optional[str] = None, limit: int = 100) -> List[InventoryHistory]:
        query = self.session.query(InventoryHistory)
        if product_id is not None:
            query = query.filter(InventoryHistory.product_id == product_id)
        if variant_id is not None:
            query = query.filter(InventoryHistory.variant_id == variant_id)
        if change_type:
            query = query.filter(InventoryHistory.change_type == change_type)
        return query.order_by(InventoryHistory.created_at.desc()).limit(limit).all()