from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.authorization import require_authentication
from app.db.session import get_db
from app.db.models import LoyaltyPoint, Referral, User

router = APIRouter(tags=["Loyalty"])


def get_current_user(auth=Depends(require_authentication)):
    return auth["user"]


@router.get("/loyalty/points")
def get_loyalty_points(db: Session = Depends(get_db), user=Depends(get_current_user)):
    """Get user's loyalty points history."""
    points = db.query(LoyaltyPoint).filter(
        LoyaltyPoint.user_id == user.id
    ).order_by(LoyaltyPoint.created_at.desc()).all()
    return points


@router.get("/loyalty/referrals")
def get_referrals(db: Session = Depends(get_db), user=Depends(get_current_user)):
    """Get user's referrals."""
    referrals = db.query(Referral).filter(
        Referral.referrer_id == user.id
    ).order_by(Referral.created_at.desc()).all()
    return referrals


@router.post("/loyalty/referrals")
def create_referral(db: Session = Depends(get_db), user=Depends(get_current_user)):
    """Create a new referral code for user."""
    import secrets
    code = f"REF-{secrets.token_hex(4).upper()}"
    referral = Referral(
        referrer_id=user.id,
        referral_code=code,
        status="pending"
    )
    db.add(referral)
    db.commit()
    db.refresh(referral)
    return referral


@router.get("/loyalty/gift-cards")
def get_gift_cards(db: Session = Depends(get_db), user=Depends(get_current_user)):
    """Get user's gift cards."""
    return []