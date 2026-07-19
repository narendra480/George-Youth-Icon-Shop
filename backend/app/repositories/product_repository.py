from typing import List, Optional
from sqlalchemy import asc, desc, func, or_
from sqlalchemy.orm import Session

from app.db.models import Brand, Category, Product, ProductImage, ProductVariant
from app.schemas.product import ProductCreate, ProductUpdate


class ProductRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def _apply_filters(
        self,
        query,
        *,
        category_id: Optional[int] = None,
        brand_id: Optional[int] = None,
        status: Optional[str] = None,
        search: Optional[str] = None,
        tags: Optional[List[str]] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
    ):
        if category_id is not None:
            query = query.filter(Product.category_id == category_id)
        if brand_id is not None:
            query = query.filter(Product.brand_id == brand_id)
        if status:
            query = query.filter(Product.status == status)
        if search:
            like = f"%{search}%"
            query = query.filter(
                or_(
                    Product.name.ilike(like),
                    Product.sku.ilike(like),
                    Product.search_keywords.ilike(like),
                    Product.tags.astext.contains(search),
                )
            )
        if tags:
            for tag in tags:
                query = query.filter(Product.tags.astext.contains(tag))
        if min_price is not None:
            query = query.filter(Product.selling_price >= min_price)
        if max_price is not None:
            query = query.filter(Product.selling_price <= max_price)
        return query

    def list_products(
        self,
        *,
        category_id: Optional[int] = None,
        brand_id: Optional[int] = None,
        status: Optional[str] = None,
        search: Optional[str] = None,
        tags: Optional[List[str]] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = "asc",
        skip: int = 0,
        limit: int = 100,
    ) -> List[Product]:
        query = (
            self.session.query(Product)
            .options(
                # Eager load common relations
            )
            .filter(Product.deleted_at.is_(None))
        )
        query = self._apply_filters(
            query,
            category_id=category_id,
            brand_id=brand_id,
            status=status,
            search=search,
            tags=tags,
            min_price=min_price,
            max_price=max_price,
        )
        col = getattr(Product, sort_by, None) if sort_by else None
        if col is not None:
            query = query.order_by(col.desc() if sort_order == "desc" else col.asc())
        return query.offset(skip).limit(limit).all()

    def count_products(
        self,
        *,
        category_id: Optional[int] = None,
        brand_id: Optional[int] = None,
        status: Optional[str] = None,
        search: Optional[str] = None,
        tags: Optional[List[str]] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
    ) -> int:
        query = self.session.query(func.count(Product.id)).filter(Product.deleted_at.is_(None))
        query = self._apply_filters(
            query,
            category_id=category_id,
            brand_id=brand_id,
            status=status,
            search=search,
            tags=tags,
            min_price=min_price,
            max_price=max_price,
        )
        return query.scalar() or 0

    def get_by_id(self, product_id: int) -> Optional[Product]:
        return (
            self.session.query(Product)
            .filter(Product.id == product_id, Product.deleted_at.is_(None))
            .first()
        )

    def get_by_slug(self, slug: str) -> Optional[Product]:
        return (
            self.session.query(Product)
            .filter(Product.slug == slug, Product.deleted_at.is_(None))
            .first()
        )

    def get_by_sku(self, sku: str) -> Optional[Product]:
        return (
            self.session.query(Product)
            .filter(Product.sku == sku, Product.deleted_at.is_(None))
            .first()
        )

    def get_by_barcode(self, barcode: str) -> Optional[Product]:
        return (
            self.session.query(Product)
            .filter(Product.barcode == barcode, Product.deleted_at.is_(None))
            .first()
        )

    def create(self, payload: ProductCreate, user_id: Optional[int] = None) -> Product:
        data = payload.model_dump(exclude={"images", "primary_image_index"})
        product = Product(**(data or {}))
        if user_id:
            product.created_by = user_id
            product.updated_by = user_id
        self.session.add(product)
        self.session.commit()
        self.session.refresh(product)

        images = payload.images or []
        primary_index = payload.primary_image_index or 0
        for idx, path in enumerate(images):
            img = ProductImage(
                product_id=product.id,
                image_path=path,
                sort_order=idx,
                is_primary=(idx == primary_index),
            )
            self.session.add(img)
        if images:
            self.session.commit()
            self.session.refresh(product)
        return product

    def update(self, product_id: int, payload: ProductUpdate, user_id: Optional[int] = None) -> Optional[Product]:
        product = self.get_by_id(product_id)
        if not product:
            return None
        data = payload.model_dump(exclude_unset=True)
        for key, value in data.items():
            setattr(product, key, value)
        if user_id:
            product.updated_by = user_id
        self.session.commit()
        self.session.refresh(product)
        return product

    def soft_delete(self, product_id: int) -> bool:
        product = self.get_by_id(product_id)
        if not product:
            return False
        from datetime import datetime
        product.deleted_at = datetime.utcnow()
        self.session.commit()
        return True

    def bulk_update_status(self, product_ids: List[int], status: str, user_id: Optional[int] = None) -> int:
        products = (
            self.session.query(Product)
            .filter(Product.id.in_(product_ids), Product.deleted_at.is_(None))
            .all()
        )
        count = 0
        for product in products:
            product.status = status
            if user_id:
                product.updated_by = user_id
            count += 1
        self.session.commit()
        return count

    def bulk_update_category(self, product_ids: List[int], category_id: int, user_id: Optional[int] = None) -> int:
        products = (
            self.session.query(Product)
            .filter(Product.id.in_(product_ids), Product.deleted_at.is_(None))
            .all()
        )
        count = 0
        for product in products:
            product.category_id = category_id
            if user_id:
                product.updated_by = user_id
            count += 1
        self.session.commit()
        return count

    def bulk_delete(self, product_ids: List[int]) -> int:
        products = (
            self.session.query(Product)
            .filter(Product.id.in_(product_ids), Product.deleted_at.is_(None))
            .all()
        )
        count = 0
        for product in products:
            product.deleted_at = func.now()
            count += 1
        self.session.commit()
        return count

    def add_images(self, product_id: int, image_paths: List[str], primary_index: Optional[int] = None) -> List[ProductImage]:
        product = self.get_by_id(product_id)
        if not product:
            return []
        existing = self.session.query(ProductImage).filter(ProductImage.product_id == product_id).count()
        created = []
        for idx, path in enumerate(image_paths):
            img = ProductImage(
                product_id=product_id,
                image_path=path,
                sort_order=existing + idx,
                is_primary=((primary_index if primary_index is not None else 0) == idx),
            )
            self.session.add(img)
            created.append(img)
        self.session.commit()
        for img in created:
            self.session.refresh(img)
        return created

    def reorder_images(self, product_id: int, image_ids_in_order: List[int]) -> bool:
        images = (
            self.session.query(ProductImage)
            .filter(ProductImage.product_id == product_id, ProductImage.id.in_(image_ids_in_order))
            .all()
        )
        if len(images) != len(image_ids_in_order):
            return False
        order_map = {img_id: idx for idx, img_id in enumerate(image_ids_in_order)}
        for img in images:
            img.sort_order = order_map[img.id]
        self.session.commit()
        return True

    def set_primary_image(self, product_id: int, image_id: Optional[int]) -> bool:
        images = self.session.query(ProductImage).filter(ProductImage.product_id == product_id).all()
        if not images:
            return False
        for img in images:
            img.is_primary = (img.id == image_id)
        if image_id is None and images:
            images[0].is_primary = True
        self.session.commit()
        return True

    def get_related(self, product: Product, limit: int = 8) -> List[Product]:
        return (
            self.session.query(Product)
            .filter(
                Product.deleted_at.is_(None),
                Product.id != product.id,
                Product.category_id == product.category_id,
            )
            .limit(limit)
            .all()
        )

    def get_brands(self) -> List[Brand]:
        return self.session.query(Brand).filter(Brand.deleted_at.is_(None)).order_by(Brand.name.asc()).all()

    def get_brand_by_slug(self, slug: str) -> Optional[Brand]:
        return self.session.query(Brand).filter(Brand.slug == slug, Brand.deleted_at.is_(None)).first()


class BrandRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, name: str, slug: str, description: Optional[str] = None, logo_url: Optional[str] = None) -> Brand:
        brand = Brand(name=name, slug=slug, description=description, logo_url=logo_url)
        self.session.add(brand)
        self.session.commit()
        self.session.refresh(brand)
        return brand

    def get_by_id(self, brand_id: int) -> Optional[Brand]:
        return self.session.query(Brand).filter(Brand.id == brand_id, Brand.deleted_at.is_(None)).first()

    def get_by_slug(self, slug: str) -> Optional[Brand]:
        return self.session.query(Brand).filter(Brand.slug == slug, Brand.deleted_at.is_(None)).first()

    def list_all(self) -> List[Brand]:
        return self.session.query(Brand).filter(Brand.deleted_at.is_(None)).order_by(Brand.name.asc()).all()

    def update(self, brand_id: int, **kwargs) -> Optional[Brand]:
        brand = self.get_by_id(brand_id)
        if not brand:
            return None
        for key, value in kwargs.items():
            if hasattr(brand, key):
                setattr(brand, key, value)
        self.session.commit()
        self.session.refresh(brand)
        return brand

    def delete(self, brand_id: int) -> bool:
        brand = self.get_by_id(brand_id)
        if not brand:
            return False
        from datetime import datetime
        brand.deleted_at = datetime.utcnow()
        self.session.commit()
        return True