from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.authorization import require_authentication, require_any_permission
from app.db.session import get_db
from app.schemas.coupon import CouponCreate, CouponUpdate, CouponResponse, CouponValidateResponse
from app.db.models import Coupon, CouponUsage

router = APIRouter(tags=["Coupons"])


@router.get("/coupons", response_model=list[CouponResponse])
def list_coupons(db: Session = Depends(get_db), auth=Depends(require_any_permission("products.manage", "admin.all"))):
    return db.query(Coupon).filter(Coupon.deleted_at.is_(None)).all()


@router.post("/coupons", response_model=CouponResponse, status_code=status.HTTP_201_CREATED)
def create_coupon(payload: CouponCreate, db: Session = Depends(get_db), auth=Depends(require_any_permission("products.manage", "admin.all"))):
    coupon = Coupon(**payload.model_dump())
    db.add(coupon)
    db.commit()
    db.refresh(coupon)
    return coupon


@router.put("/coupons/{coupon_id}", response_model=CouponResponse)
def update_coupon(coupon_id: int, payload: CouponUpdate, db: Session = Depends(get_db), auth=Depends(require_any_permission("products.manage", "admin.all"))):
    coupon = db.query(Coupon).filter(Coupon.id == coupon_id, Coupon.deleted_at.is_(None)).first()
    if not coupon:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Coupon not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(coupon, key, value)
    db.commit()
    db.refresh(coupon)
    return coupon


@router.delete("/coupons/{coupon_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_coupon(coupon_id: int, db: Session = Depends(get_db), auth=Depends(require_any_permission("products.manage", "admin.all"))):
    coupon = db.query(Coupon).filter(Coupon.id == coupon_id, Coupon.deleted_at.is_(None)).first()
    if not coupon:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Coupon not found")
    coupon.deleted_at = datetime.utcnow()
    db.commit()


@router.get("/coupons/validate", response_model=CouponValidateResponse)
def validate_coupon(code: str, db: Session = Depends(get_db), user=Depends(require_authentication)):
    coupon = db.query(Coupon).filter(Coupon.code == code, Coupon.is_active == True, Coupon.deleted_at.is_(None)).first()
    if not coupon:
        return CouponValidateResponse(valid=False, discount_amount=0.0, message="Invalid coupon")
    now = datetime.utcnow()
    if coupon.start_date and now < coupon.start_date:
        return CouponValidateResponse(valid=False, discount_amount=0.0, message="Coupon not started yet")
    if coupon.end_date and now > coupon.end_date:
        return CouponValidateResponse(valid=False, discount_amount=0.0, message="Coupon expired")
    if coupon.max_uses and coupon.used_count >= coupon.max_uses:
        return CouponValidateResponse(valid=False, discount_amount=0.0, message="Coupon usage limit exceeded")
    return CouponValidateResponse(valid=True, discount_amount=0.0, message="Valid coupon", coupon=coupon)