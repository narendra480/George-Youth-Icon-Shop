import json
import logging
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from app.db.models import ShopSettings

logger = logging.getLogger("app.shop_settings_repository")


class ShopSettingsRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_or_create(self) -> ShopSettings:
        """Get existing shop settings or create default ones"""
        settings = self.db.query(ShopSettings).first()
        if not settings:
            settings = ShopSettings()
            self.db.add(settings)
            self.db.commit()
            self.db.refresh(settings)
            logger.info("SHOP_SETTINGS | CREATED | Default shop settings created")
        return settings

    def get_by_id(self, settings_id: int) -> Optional[ShopSettings]:
        return self.db.query(ShopSettings).filter(ShopSettings.id == settings_id).first()

    def update(self, settings_id: int, data: Dict[str, Any]) -> Optional[ShopSettings]:
        settings = self.get_by_id(settings_id)
        if not settings:
            return None

        for key, value in data.items():
            if hasattr(settings, key):
                setattr(settings, key, value)

        self.db.commit()
        self.db.refresh(settings)
        logger.info(f"SHOP_SETTINGS | UPDATED | Settings id: {settings_id}")
        return settings

    def list_all(self) -> List[ShopSettings]:
        return self.db.query(ShopSettings).all()

    def delete(self, settings_id: int) -> bool:
        settings = self.get_by_id(settings_id)
        if not settings:
            return False

        self.db.delete(settings)
        self.db.commit()
        logger.info(f"SHOP_SETTINGS | DELETED | Settings id: {settings_id}")
        return True

    def get_business_hours(self, settings_id: int) -> Optional[Dict[str, Any]]:
        """Parse and return business hours as dictionary"""
        settings = self.get_by_id(settings_id)
        if not settings or not settings.business_hours:
            return None
        try:
            return json.loads(settings.business_hours)
        except json.JSONDecodeError:
            logger.warning(f"SHOP_SETTINGS | INVALID_JSON | Invalid business hours JSON")
            return None

    def set_business_hours(self, settings_id: int, hours: Dict[str, Any]) -> Optional[ShopSettings]:
        """Store business hours as JSON"""
        settings = self.get_by_id(settings_id)
        if not settings:
            return None

        settings.business_hours = json.dumps(hours)
        self.db.commit()
        self.db.refresh(settings)
        logger.info(f"SHOP_SETTINGS | BUSINESS_HOURS_UPDATED | Settings id: {settings_id}")
        return settings

    def get_phone_numbers(self, settings_id: int) -> Optional[List[str]]:
        """Parse and return phone numbers as list"""
        settings = self.get_by_id(settings_id)
        if not settings or not settings.phone_numbers:
            return None
        try:
            return json.loads(settings.phone_numbers)
        except json.JSONDecodeError:
            logger.warning(f"SHOP_SETTINGS | INVALID_JSON | Invalid phone numbers JSON")
            return None

    def set_phone_numbers(self, settings_id: int, numbers: List[str]) -> Optional[ShopSettings]:
        """Store phone numbers as JSON"""
        settings = self.get_by_id(settings_id)
        if not settings:
            return None

        settings.phone_numbers = json.dumps(numbers)
        self.db.commit()
        self.db.refresh(settings)
        logger.info(f"SHOP_SETTINGS | PHONE_NUMBERS_UPDATED | Settings id: {settings_id}")
        return settings
