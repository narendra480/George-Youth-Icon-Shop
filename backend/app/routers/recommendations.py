from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, or_

from app.core.authorization import require_authentication
from app.db.session import get_db
from app.db.models import Product, OrderItem, Order, Wishlist, RecentlyViewed, UserBehavior, Recommendation, Category

router = APIRouter(tags=["Recommendations"])


def get_current_user(auth=Depends(require_authentication)):
    return auth["user"]


@router.get("/recommendations/for-you")
def get_personalized_recommendations(
    limit: int = 10,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """Get personalized recommendations based on user behavior."""
    purchased_products = db.query(OrderItem.product_id).join(Order).filter(
        Order.user_id == user.id
    ).distinct().subquery()
    
    query = db.query(
        Product,
        (func.coalesce(Recommendation.score, 0) + func.coalesce(Product.is_trending, 0) * 0.5).label("score")
    ).outerjoin(Recommendation, Recommendation.product_id == Product.id).filter(
        ~Product.id.in_(purchased_products)
    ).order_by(func.random()).limit(limit)
    
    return query.all()


@router.get("/recommendations/similar/{product_id}")
def get_similar_products(
    product_id: int,
    limit: int = 6,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """Get similar products based on category."""
    product = db.query(Product).get(product_id)
    if not product:
        return []
    
    return db.query(Product).filter(
        Product.category_id == product.category_id,
        Product.id != product_id
    ).limit(limit).all()


@router.get("/recommendations/frequently-bought-together/{product_id}")
def get_frequently_bought_together(
    product_id: int,
    limit: int = 6,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """Get products frequently bought with this product."""
    order_ids = db.query(OrderItem.order_id).filter(
        OrderItem.product_id == product_id
    ).distinct().subquery()
    
    return db.query(Product).join(OrderItem).filter(
        OrderItem.order_id.in_(order_ids),
        OrderItem.product_id != product_id
    ).limit(limit).all()


@router.get("/recommendations/trending")
def get_trending_products(
    limit: int = 10,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """Get trending products."""
    return db.query(Product).filter(
        Product.is_trending == True,
        Product.status == "published"
    ).order_by(func.random()).limit(limit).all()


@router.get("/recommendations/recently-viewed")
def get_recently_viewed(
    limit: int = 10,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """Get user's recently viewed products."""
    return db.query(Product).join(RecentlyViewed).filter(
        RecentlyViewed.user_id == user.id
    ).order_by(RecentlyViewed.viewed_at.desc()).limit(limit).all()


@router.post("/recommendations/{product_id}/click")
def track_recommendation_click(
    product_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """Track recommendation click."""
    rec = db.query(Recommendation).filter(
        Recommendation.user_id == user.id,
        Recommendation.product_id == product_id
    ).first()
    if rec:
        rec.is_clicked = True
        db.commit()
    return {"status": "tracked"}


@router.get("/recommendations/trending/daily")
def get_daily_trending(db: Session = Depends(get_db)):
    """Get daily trending products."""
    from datetime import datetime, timedelta
    yesterday = datetime.utcnow() - timedelta(days=1)
    return db.query(Product).filter(
        Product.is_trending == True,
        Product.updated_at >= yesterday
    ).limit(10).all()


@router.get("/recommendations/trending/weekly")
def get_weekly_trending(db: Session = Depends(get_db)):
    """Get weekly trending products."""
    from datetime import datetime, timedelta
    week_ago = datetime.utcnow() - timedelta(days=7)
    return db.query(Product).filter(
        Product.is_trending == True,
        Product.updated_at >= week_ago
    ).limit(10).all()


@router.get("/recommendations/search/suggestions")
def get_search_suggestions(
    query: str,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get search suggestions."""
    return db.query(Product.name).filter(
        or_(
            Product.name.ilike(f"%{query}%"),
            Product.search_keywords.ilike(f"%{query}%")
        )
    ).distinct().limit(limit).all()