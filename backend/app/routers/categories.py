from fastapi import APIRouter, Depends, HTTPException, status

from app.core.authorization import require_authentication, require_any_permission
from app.db.models import Category, Product
from app.db.session import get_db
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from sqlalchemy import func
from sqlalchemy.orm import Session

router = APIRouter(tags=["Categories"])


DEFAULT_CATEGORIES = [
    {"name": "Men", "slug": "men", "display_order": 1},
    {"name": "Women", "slug": "women", "display_order": 2},
    {"name": "Kids", "slug": "kids", "display_order": 3},
    {"name": "Sports Shoes", "slug": "sports-shoes", "display_order": 10},
    {"name": "Running Shoes", "slug": "running-shoes", "display_order": 11},
    {"name": "Walking Shoes", "slug": "walking-shoes", "display_order": 12},
    {"name": "Casual Shoes", "slug": "casual-shoes", "display_order": 13},
    {"name": "Formal Shoes", "slug": "formal-shoes", "display_order": 14},
    {"name": "Sneakers", "slug": "sneakers", "display_order": 15},
    {"name": "Sandals", "slug": "sandals", "display_order": 16},
    {"name": "Slippers", "slug": "slippers", "display_order": 17},
    {"name": "Flip Flops", "slug": "flip-flops", "display_order": 18},
    {"name": "Boots", "slug": "boots", "display_order": 19},
    {"name": "Loafers", "slug": "loafers", "display_order": 20},
    {"name": "Heels", "slug": "heels", "display_order": 21},
    {"name": "School Shoes", "slug": "school-shoes", "display_order": 22},
    {"name": "Ethnic Footwear", "slug": "ethnic-footwear", "display_order": 23},
    {"name": "Crocs", "slug": "crocs", "display_order": 24},
    {"name": "Accessories", "slug": "accessories", "display_order": 25},
]

@router.post("/categories/seed", status_code=status.HTTP_201_CREATED)
def seed_categories(db: Session = Depends(get_db), auth=Depends(require_any_permission("products.manage", "admin.all"))):
    """Seed default footwear categories - only for initial setup."""
    existing = db.query(Category).filter(Category.deleted_at.is_(None)).count()
    if existing > 0:
        return {"message": "Categories already exist", "count": existing}
    created = []
    for cat in DEFAULT_CATEGORIES:
        obj = Category(**cat, is_active=True)
        db.add(obj)
        created.append(obj)
    db.commit()
    for obj in created:
        db.refresh(obj)
    return {"created": len(created), "categories": [c.name for c in created]}


@router.get("/categories", response_model=list[CategoryResponse])
def list_categories(db: Session = Depends(get_db)) -> list[CategoryResponse]:
    return db.query(Category).filter(Category.deleted_at.is_(None), Category.is_active == True).order_by(Category.name.asc()).all()


@router.get("/categories/with-counts")
def categories_with_counts(db: Session = Depends(get_db)):
    results = db.query(
        Category.id,
        Category.name,
        Category.slug,
        Category.description,
        Category.parent_id,
        func.count(Product.id).label("product_count"),
    ).outerjoin(
        Product, (Product.category_id == Category.id) & (Product.deleted_at.is_(None))
    ).filter(Category.deleted_at.is_(None)).group_by(Category.id).all()
    return [
        {
            "id": r.id,
            "name": r.name,
            "slug": r.slug,
            "description": r.description,
            "parent_id": r.parent_id,
            "product_count": r.product_count,
            "children": [],
        }
        for r in results
    ]


def build_category_hierarchy(categories: list[dict]) -> list[dict]:
    """Build nested category tree from flat list."""
    category_map = {c["id"]: c for c in categories}
    roots = []
    for cat in categories:
        if cat.get("parent_id"):
            parent = category_map.get(cat["parent_id"])
            if parent:
                parent.setdefault("children", []).append(cat)
        else:
            roots.append(cat)
    return roots


@router.get("/categories/hierarchy")
def categories_hierarchy(db: Session = Depends(get_db)):
    results = db.query(
        Category.id,
        Category.name,
        Category.slug,
        Category.description,
        Category.parent_id,
        Category.banner_url,
        Category.thumbnail_url,
        Category.icon_url,
        Category.is_featured,
        Category.display_order,
    ).filter(Category.deleted_at.is_(None)).order_by(Category.display_order.asc()).all()
    categories = [
        {
            "id": r.id,
            "name": r.name,
            "slug": r.slug,
            "description": r.description,
            "parent_id": r.parent_id,
            "banner_url": r.banner_url,
            "thumbnail_url": r.thumbnail_url,
            "icon_url": r.icon_url,
            "is_featured": r.is_featured,
            "display_order": r.display_order,
            "children": [],
        }
        for r in results
    ]
    return build_category_hierarchy(categories)


@router.post("/categories", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    payload: CategoryCreate,
    db: Session = Depends(get_db),
    auth=Depends(require_any_permission("products.manage", "admin.all")),
):
    category = Category(**payload.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.put("/categories/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: int,
    payload: CategoryUpdate,
    db: Session = Depends(get_db),
    auth=Depends(require_any_permission("products.manage", "admin.all")),
):
    category = db.query(Category).filter(Category.id == category_id, Category.deleted_at.is_(None)).first()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(category, key, value)
    db.commit()
    db.refresh(category)
    return category


@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    auth=Depends(require_any_permission("products.manage", "admin.all")),
):
    category = db.query(Category).filter(Category.id == category_id, Category.deleted_at.is_(None)).first()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    category.deleted_at = func.now()
    db.commit()