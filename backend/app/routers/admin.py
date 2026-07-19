from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.models import Category, Product, User
from app.db.session import get_db
from pydantic import BaseModel

router = APIRouter(tags=["Admin"])


class MetricsResponse(BaseModel):
    total_users: int
    total_products: int
    total_categories: int
    active_categories: int


@router.get("/admin/metrics", response_model=MetricsResponse)
def get_metrics(db: Session = Depends(get_db)) -> MetricsResponse:
    total_users = db.query(func.count(User.id)).scalar() or 0
    total_products = db.query(func.count(Product.id)).scalar() or 0
    total_categories = db.query(func.count(Category.id)).scalar() or 0
    active_categories = db.query(func.count(Category.id)).filter(Category.deleted_at.is_(None)).scalar() or 0
    return MetricsResponse(
        total_users=total_users,
        total_products=total_products,
        total_categories=total_categories,
        active_categories=active_categories,
    )
