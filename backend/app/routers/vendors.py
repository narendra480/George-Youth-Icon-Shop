from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import secrets

from app.core.authorization import require_authentication, require_any_permission
from app.db.session import get_db
from app.db.models import Vendor, User

router = APIRouter(tags=["Vendors"])


def get_current_user(auth=Depends(require_authentication)):
    return auth["user"]


def generate_vendor_code() -> str:
    return f"VEN-{secrets.token_hex(4).upper()}"


@router.get("/vendors")
def list_vendors(db: Session = Depends(get_db), user=Depends(require_any_permission("vendors.manage", "admin.all"))):
    """List all vendors (admin only)."""
    return db.query(Vendor).all()


@router.get("/vendors/me")
def get_my_vendor(db: Session = Depends(get_db), user=Depends(get_current_user)):
    """Get current vendor profile."""
    vendor = db.query(Vendor).filter(Vendor.user_id == user.id).first()
    return vendor


@router.post("/vendors/apply")
def apply_vendor(payload: dict, db: Session = Depends(get_db), user=Depends(get_current_user)):
    """Apply for vendor registration."""
    existing = db.query(Vendor).filter(Vendor.user_id == user.id).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Already applied")
    
    vendor = Vendor(
        user_id=user.id,
        vendor_code=generate_vendor_code(),
        shop_name=payload.get("shop_name"),
        status="pending",
        gstin=payload.get("gstin"),
        pan=payload.get("pan"),
        bank_account=payload.get("bank_account")
    )
    db.add(vendor)
    db.commit()
    db.refresh(vendor)
    return vendor


@router.put("/vendors/{vendor_id}")
def update_vendor(
    vendor_id: int,
    payload: dict,
    db: Session = Depends(get_db),
    user=Depends(require_any_permission("vendors.manage", "admin.all"))
):
    """Update vendor (admin only)."""
    vendor = db.query(Vendor).get(vendor_id)
    if not vendor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vendor not found")
    
    for key, value in payload.items():
        if hasattr(vendor, key):
            setattr(vendor, key, value)
    
    db.commit()
    db.refresh(vendor)
    return vendor


@router.get("/vendors/{vendor_id}/dashboard")
def get_vendor_dashboard(
    vendor_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """Get vendor dashboard analytics."""
    vendor = db.query(Vendor).filter(
        Vendor.id == vendor_id,
        Vendor.user_id == user.id
    ).first()
    if not vendor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vendor not found")
    
    return {
        "order_count": 0,
        "revenue": 0,
        "rating": vendor.rating,
        "pending_settlements": 0
    }


@router.get("/franchises")
def list_franchises(db: Session = Depends(get_db), user=Depends(require_any_permission("franchises.manage", "admin.all"))):
    """List all franchises."""
    from app.db.models import Franchise
    return db.query(Franchise).all()


@router.post("/franchises")
def create_franchise(
    payload: dict,
    db: Session = Depends(get_db),
    user=Depends(require_any_permission("franchises.manage", "admin.all"))
):
    """Create franchise store."""
    from app.db.models import Franchise
    franchise = Franchise(
        store_name=payload.get("store_name"),
        store_code=f"STO-{secrets.token_hex(4).upper()}",
        address=payload.get("address"),
        city=payload.get("city"),
        state=payload.get("state"),
        pincode=payload.get("pincode"),
        manager_name=payload.get("manager_name"),
        manager_phone=payload.get("manager_phone")
    )
    db.add(franchise)
    db.commit()
    db.refresh(franchise)
    return franchise


@router.get("/settlements")
def list_settlements(
    db: Session = Depends(get_db),
    user=Depends(require_any_permission("settlements.manage", "admin.all"))
):
    """List settlements."""
    from app.db.models import Settlement
    return db.query(Settlement).all()