from fastapi import APIRouter, Depends, HTTPException, Query, status, File, UploadFile, Form
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload, selectinload

from app.core.authorization import require_authentication, require_any_permission
from app.db.models import Product, ProductImage, ProductVariant, Inventory
from app.db.session import get_db
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse, ProductImageResponse, ProductVariantResponse
from app.services.product_service import ProductService

router = APIRouter(tags=["Products"])


def _build_product_response(product: Product) -> dict:
    images = [
        ProductImageResponse(
            id=img.id,
            image_path=img.image_path,
            alt_text=img.alt_text,
            sort_order=img.sort_order,
            is_primary=img.is_primary,
            created_at=img.created_at,
        ).dict()
        for img in sorted(product.images, key=lambda x: x.sort_order)
    ]
    variants = [
        ProductVariantResponse(
            id=v.id,
            sku=v.sku,
            name=v.name,
            attributes=v.attributes,
            images=v.images,
            price=v.price,
            mrp=v.mrp,
            inventory_quantity=v.inventory_quantity,
            is_active=v.is_active,
            created_at=v.created_at,
            updated_at=v.updated_at,
        ).dict()
        for v in product.variants if not v.deleted_at
    ]

    category = None
    brand = None
    if getattr(product, "category", None):
        category = {"id": product.category.id, "name": product.category.name, "slug": product.category.slug}
    if getattr(product, "brand", None):
        brand = {"id": product.brand.id, "name": product.brand.name, "slug": product.brand.slug}

    base = ProductResponse.from_orm(product).dict()
    base["images"] = images
    base["variants"] = variants
    base["category"] = category
    base["brand"] = brand

    mrp = base.get("mrp")
    selling_price = base.get("selling_price")
    offer_price = base.get("offer_price")
    discount = base.get("discount_percentage") or 0.0
    effective_price = offer_price if offer_price is not None else selling_price
    you_save = None
    if mrp is not None and effective_price is not None:
        you_save = max(0.0, mrp - effective_price)
    base["you_save"] = round(you_save, 2) if you_save is not None else None

    available_stock = sum((inv.current_stock - inv.reserved_stock) for inv in product.inventories if not inv.variant_id)
    base["available_stock"] = max(0, available_stock)
    return base


@router.post("/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    payload: ProductCreate,
    db: Session = Depends(get_db),
    auth=Depends(require_any_permission("products.create", "products.manage")),
):
    service = ProductService(db)
    try:
        product = service.create_product(payload, user_id=auth["user"].id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    return _build_product_response(product)


@router.get("/products", response_model=list[ProductResponse])
def list_products(
    category_id: int | None = None,
    brand_id: int | None = None,
    status: str | None = None,
    search: str | None = None,
    tags: str | None = Query(None, description="Comma separated tags"),
    min_price: float | None = None,
    max_price: float | None = None,
    sort_by: str | None = Query(None, regex="^(price|name|created_at|mrp|selling_price)$"),
    sort_order: str | None = Query("asc", regex="^(asc|desc)$"),
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
) -> list[ProductResponse]:
    tag_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else None
    service = ProductService(db)
    items = service.list_products(
        category_id=category_id,
        brand_id=brand_id,
        status=status,
        search=search,
        tags=tag_list,
        min_price=min_price,
        max_price=max_price,
        sort_by=sort_by,
        sort_order=sort_order,
        skip=skip,
        limit=limit,
    )
    return [_build_product_response(p) for p in items]


@router.get("/products/count")
def count_products(
    category_id: int | None = None,
    brand_id: int | None = None,
    status: str | None = None,
    search: str | None = None,
    tags: str | None = Query(None),
    min_price: float | None = None,
    max_price: float | None = None,
    db: Session = Depends(get_db),
):
    tag_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else None
    service = ProductService(db)
    total = service.count_products(
        category_id=category_id,
        brand_id=brand_id,
        status=status,
        search=search,
        tags=tag_list,
        min_price=min_price,
        max_price=max_price,
    )
    return {"total": total}


@router.get("/products/featured", response_model=list[ProductResponse])
def featured_products(limit: int = 8, db: Session = Depends(get_db)) -> list[ProductResponse]:
    service = ProductService(db)
    items = service.list_products(status="active", sort_by="created_at", sort_order="desc", limit=limit)
    items = [p for p in items if p.is_featured][:limit]
    return [_build_product_response(p) for p in items]


@router.get("/products/new-arrivals", response_model=list[ProductResponse])
def new_arrivals(limit: int = 8, db: Session = Depends(get_db)) -> list[ProductResponse]:
    service = ProductService(db)
    items = service.list_products(status="active", sort_by="created_at", sort_order="desc", limit=limit)
    items = [p for p in items if p.is_new_arrival][:limit]
    return [_build_product_response(p) for p in items]


@router.get("/products/trending", response_model=list[ProductResponse])
def trending_products(limit: int = 8, db: Session = Depends(get_db)) -> list[ProductResponse]:
    service = ProductService(db)
    items = service.list_products(status="active", sort_by="created_at", sort_order="desc", limit=limit)
    items = [p for p in items if p.is_trending][:limit]
    return [_build_product_response(p) for p in items]


@router.get("/products/recommended", response_model=list[ProductResponse])
def recommended_products(limit: int = 8, db: Session = Depends(get_db)) -> list[ProductResponse]:
    service = ProductService(db)
    items = service.list_products(status="active", sort_by="created_at", sort_order="desc", limit=limit)
    items = [p for p in items if p.is_featured or p.is_best_seller or p.is_trending][:limit]
    return [_build_product_response(p) for p in items]


@router.get("/products/best-sellers", response_model=list[ProductResponse])
def best_sellers(limit: int = 8, db: Session = Depends(get_db)) -> list[ProductResponse]:
    service = ProductService(db)
    items = service.list_products(status="active", sort_by="created_at", sort_order="desc", limit=limit)
    items = [p for p in items if p.is_best_seller][:limit]
    return [_build_product_response(p) for p in items]


@router.get("/products/slug/{slug}", response_model=ProductResponse)
def get_product_by_slug(slug: str, db: Session = Depends(get_db)) -> ProductResponse:
    service = ProductService(db)
    product = service.get_product_by_slug(slug)
    if not product or product.deleted_at:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return _build_product_response(product)


@router.get("/products/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)) -> ProductResponse:
    service = ProductService(db)
    product = service.get_product(product_id)
    if not product or product.deleted_at:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return _build_product_response(product)


@router.get("/products/{product_id}/related", response_model=list[ProductResponse])
def get_related_products(product_id: int, limit: int = 8, db: Session = Depends(get_db)) -> list[ProductResponse]:
    service = ProductService(db)
    items = service.get_related_products(product_id, limit=limit)
    return [_build_product_response(p) for p in items]


@router.put("/products/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    payload: ProductUpdate,
    db: Session = Depends(get_db),
    auth=Depends(require_any_permission("products.update", "products.manage")),
):
    service = ProductService(db)
    product = service.update_product(product_id, payload, user_id=auth["user"].id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return _build_product_response(product)


@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    auth=Depends(require_any_permission("products.delete", "products.manage")),
):
    service = ProductService(db)
    ok = service.delete_product(product_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")


@router.post("/products/{product_id}/images", response_model=ProductImageResponse)
def add_product_image(
    product_id: int,
    image_path: str = Form(...),
    alt_text: str | None = Form(None),
    is_primary: bool = Form(False),
    db: Session = Depends(get_db),
    auth=Depends(require_any_permission("products.update", "products.manage")),
):
    service = ProductService(db)
    product = service.get_product(product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    imgs = service.add_images(product_id, [image_path], primary_index=0 if is_primary else None)
    if not imgs:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unable to add image")
    created = imgs[0]
    if is_primary:
        service.set_primary_image(product_id, created.id)
        created.is_primary = True
    return ProductImageResponse.from_orm(created)


@router.put("/products/{product_id}/images/reorder")
def reorder_product_images(
    product_id: int,
    image_ids: list[int],
    db: Session = Depends(get_db),
    auth=Depends(require_any_permission("products.update", "products.manage")),
):
    service = ProductService(db)
    if not service.reorder_images(product_id, image_ids):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid image ids")
    return {"ok": True}


@router.put("/products/images/{image_id}/primary")
def set_primary_image(
    product_id: int,
    image_id: int,
    db: Session = Depends(get_db),
    auth=Depends(require_any_permission("products.update", "products.manage")),
):
    service = ProductService(db)
    if not service.set_primary_image(product_id, image_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unable to update primary image")
    return {"ok": True}


@router.post("/products/bulk/status")
def bulk_update_status(
    product_ids: list[int],
    status: str,
    db: Session = Depends(get_db),
    auth=Depends(require_any_permission("products.update", "products.manage")),
):
    if status not in {"draft", "active", "out_of_stock", "archived"}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid status")
    service = ProductService(db)
    count = service.bulk_update_status(product_ids, status, user_id=auth["user"].id)
    return {"updated": count}


@router.post("/products/bulk/category")
def bulk_update_category(
    product_ids: list[int],
    category_id: int,
    db: Session = Depends(get_db),
    auth=Depends(require_any_permission("products.update", "products.manage")),
):
    service = ProductService(db)
    count = service.bulk_update_category(product_ids, category_id, user_id=auth["user"].id)
    return {"updated": count}


@router.post("/products/bulk/delete")
def bulk_delete(
    product_ids: list[int],
    db: Session = Depends(get_db),
    auth=Depends(require_any_permission("products.delete", "products.manage")),
):
    service = ProductService(db)
    count = service.bulk_delete(product_ids)
    return {"deleted": count}


# ==========================
# Brands
# ==========================

@router.post("/brands")
def create_brand(
    name: str = Form(...),
    slug: str | None = Form(None),
    description: str | None = Form(None),
    logo_url: str | None = Form(None),
    db: Session = Depends(get_db),
    auth=Depends(require_any_permission("products.manage", "admin.all")),
):
    service = ProductService(db)
    try:
        brand = service.create_brand(name=name, slug=slug, description=description, logo_url=logo_url)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    return {"id": brand.id, "name": brand.name, "slug": brand.slug}


@router.get("/brands")
def list_brands(db: Session = Depends(get_db)) -> list[dict]:
    service = ProductService(db)
    brands = service.list_brands()
    return [{"id": b.id, "name": b.name, "slug": b.slug, "description": b.description} for b in brands]