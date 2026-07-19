from typing import Any, Optional
from uuid import uuid4

from sqlalchemy.orm import Session

from app.db.models import Brand, Product, ProductImage, ProductVariant
from app.repositories.product_repository import ProductRepository, BrandRepository
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse, compute_offer_snapshot


class ProductService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = ProductRepository(db)
        self.brand_repo = BrandRepository(db)

    def _auto_generate_sku(self) -> str:
        prefix = "PRD"
        count = self.db.query(Product).count() + 1
        return f"{prefix}-{str(count).zfill(6)}"

    def _auto_generate_slug(self, name: str) -> str:
        import re
        slug = name.lower()
        slug = re.sub(r"[^a-z0-9]+", "-", slug)
        slug = slug.strip("-")
        return slug

    def _apply_snapshot(self, product: Product, snapshot: dict[str, Any]) -> Product:
        product.discount_percentage = snapshot["discount_percentage"]
        product.offer_price = snapshot.get("effective_offer_price")
        if snapshot.get("you_save") is not None:
            product.selling_price = round(product.mrp - snapshot["you_save"], 2)
        return product

    def list_products(self, **filters):
        return self.repo.list_products(**filters)

    def count_products(self, **filters):
        return self.repo.count_products(**filters)

    def get_product(self, product_id: int) -> Optional[Product]:
        return self.repo.get_by_id(product_id)

    def get_product_by_slug(self, slug: str) -> Optional[Product]:
        return self.repo.get_by_slug(slug)

    def create_product(self, payload: ProductCreate, user_id: Optional[int] = None) -> Product:
        data = payload.model_dump()
        if not data.get("sku"):
            data["sku"] = self._auto_generate_sku()
        if not data.get("slug"):
            data["slug"] = self._auto_generate_slug(data["name"])

        sku_exists = self.repo.get_by_sku(data["sku"])
        if sku_exists:
            raise ValueError(f"SKU already exists: {data['sku']}")

        product = Product(**data)
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)

        images = payload.images or []
        primary_index = payload.primary_image_index or 0
        for idx, path in enumerate(images):
            img = ProductImage(
                product_id=product.id,
                image_path=path,
                sort_order=idx,
                is_primary=(idx == primary_index),
            )
            self.db.add(img)
        if images:
            self.db.commit()
            self.db.refresh(product)
        return product

    def update_product(self, product_id: int, payload: ProductUpdate, user_id: Optional[int] = None) -> Optional[Product]:
        product = self.repo.get_by_id(product_id)
        if not product:
            return None
        data = payload.model_dump(exclude_unset=True)
        for key, value in data.items():
            setattr(product, key, value)
        if user_id:
            product.updated_by = user_id
        self.db.commit()
        self.db.refresh(product)
        return product

    def delete_product(self, product_id: int) -> bool:
        return self.repo.soft_delete(product_id)

    def add_images(self, product_id: int, image_paths: list[str], primary_index: Optional[int] = None):
        return self.repo.add_images(product_id, image_paths, primary_index)

    def reorder_images(self, product_id: int, image_ids: list[int]) -> bool:
        return self.repo.reorder_images(product_id, image_ids)

    def set_primary_image(self, product_id: int, image_id: Optional[int]) -> bool:
        return self.repo.set_primary_image(product_id, image_id)

    def bulk_update_status(self, product_ids: list[int], status: str, user_id: Optional[int] = None) -> int:
        return self.repo.bulk_update_status(product_ids, status, user_id)

    def bulk_update_category(self, product_ids: list[int], category_id: int, user_id: Optional[int] = None) -> int:
        return self.repo.bulk_update_category(product_ids, category_id, user_id)

    def bulk_delete(self, product_ids: list[int]) -> int:
        return self.repo.bulk_delete(product_ids)

    def get_related_products(self, product_id: int, limit: int = 8) -> list[Product]:
        product = self.repo.get_by_id(product_id)
        if not product:
            return []
        return self.repo.get_related(product, limit)

    def list_brands(self) -> list[Brand]:
        return self.repo.get_brands()

    def get_brand(self, brand_id: int) -> Optional[Brand]:
        return self.brand_repo.get_by_id(brand_id)

    def create_brand(self, name: str, slug: Optional[str], description: Optional[str], logo_url: Optional[str]) -> Brand:
        import re
        if not slug:
            slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
        existing = self.brand_repo.get_by_slug(slug)
        if existing:
            raise ValueError(f"Brand slug already exists: {slug}")
        return self.brand_repo.create(name=name, slug=slug, description=description, logo_url=logo_url)

    def update_brand(self, brand_id: int, **kwargs) -> Optional[Brand]:
        return self.brand_repo.update(brand_id, **kwargs)