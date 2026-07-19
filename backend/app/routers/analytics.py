from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, or_

from app.core.authorization import require_authentication, require_any_permission
from app.db.session import get_db
from app.db.models import Order, Product, User, Inventory, Supplier, PurchaseOrder, Warehouse, Payment, ReturnRequest

router = APIRouter(tags=["Analytics"])


def get_current_user(auth=Depends(require_authentication)):
    return auth["user"]


@router.get("/analytics/dashboard")
def get_dashboard_analytics(db: Session = Depends(get_db), user=Depends(get_current_user)):
    """Get executive dashboard analytics."""
    today = datetime.utcnow().date()
    yesterday = today - timedelta(days=1)
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    year_ago = today - timedelta(days=365)
    
    # Sales data
    today_sales = db.query(func.sum(Order.total_amount)).filter(
        func.date(Order.created_at) == today
    ).scalar() or 0
    
    yesterday_sales = db.query(func.sum(Order.total_amount)).filter(
        func.date(Order.created_at) == yesterday
    ).scalar() or 0
    
    monthly_sales = db.query(func.sum(Order.total_amount)).filter(
        Order.created_at >= month_ago
    ).scalar() or 0
    
    total_sales = db.query(func.sum(Order.total_amount)).scalar() or 0
    total_orders = db.query(func.count(Order.id)).scalar() or 0
    
    pending_orders = db.query(func.count(Order.id)).filter(
        Order.status == "pending"
    ).scalar() or 0
    
    cancelled_orders = db.query(func.count(Order.id)).filter(
        Order.status == "cancelled"
    ).scalar() or 0
    
    avg_order_value = (total_sales / total_orders) if total_orders > 0 else 0
    
    # Customer data
    total_customers = db.query(func.count(User.id)).filter(
        User.is_superuser == False
    ).scalar() or 0
    
    # Inventory data
    total_products = db.query(func.count(Product.id)).scalar() or 0
    out_of_stock = db.query(func.count(Inventory.id)).filter(
        Inventory.current_stock <= 0
    ).scalar() or 0
    
    low_stock = db.query(func.count(Inventory.id)).filter(
        Inventory.current_stock > 0,
        Inventory.current_stock <= Inventory.reorder_level
    ).scalar() or 0
    
    # Supplier data
    total_suppliers = db.query(func.count(Supplier.id)).filter(
        Supplier.deleted_at == None
    ).scalar() or 0
    
    pending_pos = db.query(func.count(PurchaseOrder.id)).filter(
        PurchaseOrder.status.in_(["draft", "submitted", "approved"])
    ).scalar() or 0
    
    return {
        "sales": {
            "today": today_sales,
            "yesterday": yesterday_sales,
            "this_month": monthly_sales,
            "total": total_sales,
            "average_order_value": avg_order_value,
        },
        "orders": {
            "total": total_orders,
            "pending": pending_orders,
            "cancelled": cancelled_orders,
        },
        "customers": {
            "total": total_customers,
        },
        "inventory": {
            "total_products": total_products,
            "out_of_stock": out_of_stock,
            "low_stock": low_stock,
        },
        "suppliers": {
            "total": total_suppliers,
            "pending_pos": pending_pos,
        }
    }


@router.get("/analytics/sales")
def get_sales_analytics(
    period: Optional[str] = "month",
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """Get sales analytics with period filter."""
    now = datetime.utcnow()
    if period == "today":
        start_date = now.date()
        query = db.query(func.date(Order.created_at).label("date"), func.sum(Order.total_amount).label("sales")).filter(
            func.date(Order.created_at) == start_date
        )
    elif period == "week":
        start_date = now - timedelta(days=7)
        query = db.query(func.date(Order.created_at).label("date"), func.sum(Order.total_amount).label("sales")).filter(
            Order.created_at >= start_date
        )
    elif period == "year":
        start_date = now - timedelta(days=365)
        query = db.query(func.date(Order.created_at).label("date"), func.sum(Order.total_amount).label("sales")).filter(
            Order.created_at >= start_date
        )
    else:  # month
        start_date = now - timedelta(days=30)
        query = db.query(func.date(Order.created_at).label("date"), func.sum(Order.total_amount).label("sales")).filter(
            Order.created_at >= start_date
        )
    
    data = query.group_by(func.date(Order.created_at)).all()
    return [{"date": d[0], "sales": float(d[1] or 0)} for d in data]


@router.get("/analytics/products/top")
def get_top_products(db: Session = Depends(get_db), user=Depends(get_current_user)):
    """Get top selling products."""
    return db.query(
        Product.id,
        Product.name,
        func.sum(OrderItem.quantity).label("quantity_sold")
    ).join("order_items").group_by(Product.id).order_by(
        func.sum(OrderItem.quantity).desc()
    ).limit(10).all()


@router.get("/analytics/inventory/low-stock")
def get_low_stock_products(db: Session = Depends(get_db), user=Depends(get_current_user)):
    """Get products with low stock."""
    return db.query(
        Product.id,
        Product.name,
        Inventory.current_stock,
        Inventory.reorder_level
    ).join(Inventory).filter(
        Inventory.current_stock <= Inventory.reorder_level,
        Inventory.current_stock > 0
    ).all()


@router.get("/analytics/customers")
def get_customer_analytics(db: Session = Depends(get_db), user=Depends(get_current_user)):
    """Get customer analytics."""
    return {
        "total": db.query(func.count(User.id)).filter(User.is_superuser == False).scalar() or 0,
        "new_this_month": db.query(func.count(User.id)).filter(
            User.is_superuser == False,
            User.created_at >= datetime.utcnow() - timedelta(days=30)
        ).scalar() or 0,
    }