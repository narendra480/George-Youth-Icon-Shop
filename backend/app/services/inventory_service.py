from typing import List, Optional

from sqlalchemy.orm import Session

from app.db.models import Inventory, InventoryHistory, Product, ProductVariant
from app.repositories.inventory_repository import InventoryRepository
from app.schemas.inventory import InventoryCreate, InventoryUpdate, InventoryResponse, InventoryHistoryResponse


class InventoryService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = InventoryRepository(db)

    def get_inventory(self, product_id: int, variant_id: Optional[int] = None) -> Optional[Inventory]:
        return self.repo.get_inventory(product_id, variant_id)

    def list_inventories(self, product_id: Optional[int] = None, variant_id: Optional[int] = None, low_stock_only: bool = False) -> List[Inventory]:
        return self.repo.list_inventories(product_id=product_id, variant_id=variant_id, low_stock_only=low_stock_only)

    def create_or_update_inventory(self, product_id: int, variant_id: Optional[int], current_stock: int, reserved_stock: int = 0, reorder_level: int = 0, low_stock_alert: bool = False) -> Inventory:
        return self.repo.create_or_update(product_id, variant_id, current_stock, reserved_stock, reorder_level, low_stock_alert)

    def stock_in(self, product_id: int, quantity: int, variant_id: Optional[int] = None, created_by: Optional[int] = None, reference_id: Optional[str] = None, notes: Optional[str] = None) -> Optional[Inventory]:
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        return self.repo.adjust_stock(product_id, variant_id, quantity, "stock_in", created_by=created_by, reference_id=reference_id, notes=notes)

    def stock_out(self, product_id: int, quantity: int, variant_id: Optional[int] = None, created_by: Optional[int] = None, reference_id: Optional[str] = None, notes: Optional[str] = None) -> Optional[Inventory]:
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        return self.repo.adjust_stock(product_id, variant_id, -quantity, "stock_out", created_by=created_by, reference_id=reference_id, notes=notes)

    def adjust_stock(self, product_id: int, new_stock: int, variant_id: Optional[int] = None, created_by: Optional[int] = None, notes: Optional[str] = None) -> Optional[Inventory]:
        inventory = self.repo.get_inventory(product_id, variant_id)
        previous = inventory.current_stock if inventory else 0
        quantity_change = new_stock - previous
        return self.repo.adjust_stock(product_id, variant_id, quantity_change, "adjustment", created_by=created_by, notes=notes)

    def get_history(self, product_id: Optional[int] = None, variant_id: Optional[int] = None, change_type: Optional[str] = None, limit: int = 100) -> List[InventoryHistory]:
        return self.repo.get_history(product_id=product_id, variant_id=variant_id, change_type=change_type, limit=limit)