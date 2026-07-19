import json
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from app.db.models import ShopSettings
from app.repositories.shop_settings_repository import ShopSettingsRepository

logger = logging.getLogger("app.shop_settings_service")


class ShopSettingsService:
    """Service for managing shop configuration and settings"""

    def __init__(self, db: Session):
        self.db = db
        self.repo = ShopSettingsRepository(db)
        self._cache: Optional[ShopSettings] = None

    def get_settings(self) -> ShopSettings:
        """Get or create shop settings (with caching)"""
        if not self._cache:
            self._cache = self.repo.get_or_create()
        return self._cache

    def update_settings(self, data: Dict[str, Any]) -> ShopSettings:
        """Update shop settings"""
        settings = self.get_settings()
        
        # Validate JSON fields
        if "business_hours" in data and isinstance(data["business_hours"], dict):
            data["business_hours"] = json.dumps(data["business_hours"])

        if "phone_numbers" in data and isinstance(data["phone_numbers"], list):
            data["phone_numbers"] = json.dumps(data["phone_numbers"])

        updated = self.repo.update(settings.id, data)
        
        # Invalidate cache
        self._cache = None
        
        logger.info("SHOP_SETTINGS | UPDATED | Settings updated successfully")
        return updated

    def get_business_hours(self) -> Optional[Dict[str, Any]]:
        """Get business hours as structured dict"""
        settings = self.get_settings()
        return self.repo.get_business_hours(settings.id)

    def set_business_hours(self, hours: Dict[str, Any]) -> ShopSettings:
        """Set business hours from structured dict"""
        settings = self.get_settings()
        return self.repo.set_business_hours(settings.id, hours)

    def get_phone_numbers(self) -> Optional[List[str]]:
        """Get phone numbers as list"""
        settings = self.get_settings()
        return self.repo.get_phone_numbers(settings.id)

    def set_phone_numbers(self, numbers: List[str]) -> ShopSettings:
        """Set phone numbers from list"""
        settings = self.get_settings()
        return self.repo.set_phone_numbers(settings.id, numbers)

    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary (for API responses)"""
        settings = self.get_settings()
        return {
            "id": settings.id,
            "shop_name": settings.shop_name,
            "tagline": settings.tagline,
            "description": settings.description,
            "owner_name": settings.owner_name,
            "logo_url": settings.logo_url,
            "favicon_url": settings.favicon_url,
            "hero_banner_url": settings.hero_banner_url,
            "primary_phone": settings.primary_phone,
            "phone_numbers": self.get_phone_numbers() if settings.phone_numbers else None,
            "whatsapp": settings.whatsapp,
            "email": settings.email,
            "address": settings.address,
            "city": settings.city,
            "state": settings.state,
            "country": settings.country,
            "postal_code": settings.postal_code,
            "business_hours": self.get_business_hours() if settings.business_hours else None,
            "google_maps_url": settings.google_maps_url,
            "facebook_url": settings.facebook_url,
            "instagram_url": settings.instagram_url,
            "youtube_url": settings.youtube_url,
            "twitter_url": settings.twitter_url,
            "linkedin_url": settings.linkedin_url,
            "footer_text": settings.footer_text,
            "copyright_text": settings.copyright_text,
            "privacy_policy_url": settings.privacy_policy_url,
            "terms_url": settings.terms_url,
            "faq_url": settings.faq_url,
            "created_at": settings.created_at,
            "updated_at": settings.updated_at,
        }
