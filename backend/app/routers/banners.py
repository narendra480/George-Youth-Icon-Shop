from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.authorization import require_authentication, require_any_permission
from app.db.session import get_db
from app.schemas.banner import BannerCreate, BannerUpdate, BannerResponse
from app.db.models import Banner

router = APIRouter(tags=["Banners"])


@router.get("/banners", response_model=list[BannerResponse])
def list_banners(position: str | None = None, db: Session = Depends(get_db)):
    query = db.query(Banner).filter(Banner.deleted_at.is_(None), Banner.is_active == True)
    if position:
        query = query.filter(Banner.position == position)
    now = datetime.utcnow()
    query = query.filter(
        (Banner.start_date.is_(None) | (Banner.start_date <= now)),
        (Banner.end_date.is_(None) | (Banner.end_date >= now))
    )
    return query.order_by(Banner.sort_order.asc()).all()


@router.get("/banners/hero", response_model=list[BannerResponse])
def hero_banners(db: Session = Depends(get_db)):
    now = datetime.utcnow()
    query = db.query(Banner).filter(
        Banner.deleted_at.is_(None),
        Banner.is_active == True,
        Banner.banner_type == "hero",
        (Banner.start_date.is_(None) | (Banner.start_date <= now)),
        (Banner.end_date.is_(None) | (Banner.end_date >= now))
    ).order_by(Banner.sort_order.asc())
    banners = query.all()
    if not banners:
        default_banner = Banner(
            title="Welcome to George's Youth Icon Shop",
            subtitle="Premium Footwear Collection",
            description="Discover the latest trends in footwear. Flat 50% OFF on new arrivals.",
            image_url="/hero-default.jpg",
            banner_type="hero",
            position="home",
            background_color="#1E3A8A",
            text_color="#ffffff",
            is_active=True,
            sort_order=0,
        )
        db.add(default_banner)
        db.commit()
        db.refresh(default_banner)
        banners = [default_banner]
    for b in banners:
        b.view_count = (b.view_count or 0) + 1
    db.commit()
    return banners


@router.post("/banners", response_model=BannerResponse, status_code=status.HTTP_201_CREATED)
def create_banner(payload: BannerCreate, db: Session = Depends(get_db), auth=Depends(require_any_permission("products.manage", "admin.all"))):
    banner = Banner(**payload.model_dump())
    db.add(banner)
    db.commit()
    db.refresh(banner)
    return banner


@router.put("/banners/{banner_id}", response_model=BannerResponse)
def update_banner(banner_id: int, payload: BannerUpdate, db: Session = Depends(get_db), auth=Depends(require_any_permission("products.manage", "admin.all"))):
    banner = db.query(Banner).filter(Banner.id == banner_id, Banner.deleted_at.is_(None)).first()
    if not banner:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Banner not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(banner, key, value)
    db.commit()
    db.refresh(banner)
    return banner


@router.delete("/banners/{banner_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_banner(banner_id: int, db: Session = Depends(get_db), auth=Depends(require_any_permission("products.manage", "admin.all"))):
    banner = db.query(Banner).filter(Banner.id == banner_id, Banner.deleted_at.is_(None)).first()
    if not banner:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Banner not found")
    banner.deleted_at = datetime.utcnow()
    db.commit()