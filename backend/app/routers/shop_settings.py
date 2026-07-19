from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.shop_settings_service import ShopSettingsService

router = APIRouter(tags=["Shop Settings"])


@router.get("/shop-settings/public")
def get_public_settings(db: Session = Depends(get_db)):
    service = ShopSettingsService(db)
    return service.to_dict()