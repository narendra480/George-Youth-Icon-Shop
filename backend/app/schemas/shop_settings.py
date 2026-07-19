from datetime import datetime
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Dict, Any


class ShopSettingsBase(BaseModel):
    shop_name: str = Field(..., min_length=1, max_length=255)
    tagline: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    owner_name: Optional[str] = Field(None, max_length=255)
    logo_url: Optional[str] = Field(None, max_length=512)
    favicon_url: Optional[str] = Field(None, max_length=512)
    hero_banner_url: Optional[str] = Field(None, max_length=512)
    primary_phone: Optional[str] = Field(None, max_length=32)
    phone_numbers: Optional[str] = None  # JSON string
    whatsapp: Optional[str] = Field(None, max_length=32)
    email: Optional[EmailStr] = None
    address: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, max_length=128)
    state: Optional[str] = Field(None, max_length=128)
    country: Optional[str] = Field(None, max_length=128)
    postal_code: Optional[str] = Field(None, max_length=32)
    business_hours: Optional[str] = None  # JSON string
    google_maps_url: Optional[str] = Field(None, max_length=512)
    google_maps_embed: Optional[str] = None
    facebook_url: Optional[str] = Field(None, max_length=512)
    instagram_url: Optional[str] = Field(None, max_length=512)
    youtube_url: Optional[str] = Field(None, max_length=512)
    twitter_url: Optional[str] = Field(None, max_length=512)
    linkedin_url: Optional[str] = Field(None, max_length=512)
    footer_text: Optional[str] = None
    copyright_text: Optional[str] = Field(None, max_length=255)
    privacy_policy_url: Optional[str] = Field(None, max_length=512)
    terms_url: Optional[str] = Field(None, max_length=512)
    faq_url: Optional[str] = Field(None, max_length=512)


class ShopSettingsCreate(ShopSettingsBase):
    pass


class ShopSettingsUpdate(BaseModel):
    shop_name: Optional[str] = Field(None, min_length=1, max_length=255)
    tagline: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    owner_name: Optional[str] = Field(None, max_length=255)
    logo_url: Optional[str] = Field(None, max_length=512)
    favicon_url: Optional[str] = Field(None, max_length=512)
    hero_banner_url: Optional[str] = Field(None, max_length=512)
    primary_phone: Optional[str] = Field(None, max_length=32)
    phone_numbers: Optional[str] = None
    whatsapp: Optional[str] = Field(None, max_length=32)
    email: Optional[EmailStr] = None
    address: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, max_length=128)
    state: Optional[str] = Field(None, max_length=128)
    country: Optional[str] = Field(None, max_length=128)
    postal_code: Optional[str] = Field(None, max_length=32)
    business_hours: Optional[str] = None
    google_maps_url: Optional[str] = Field(None, max_length=512)
    google_maps_embed: Optional[str] = None
    facebook_url: Optional[str] = Field(None, max_length=512)
    instagram_url: Optional[str] = Field(None, max_length=512)
    youtube_url: Optional[str] = Field(None, max_length=512)
    twitter_url: Optional[str] = Field(None, max_length=512)
    linkedin_url: Optional[str] = Field(None, max_length=512)
    footer_text: Optional[str] = None
    copyright_text: Optional[str] = Field(None, max_length=255)
    privacy_policy_url: Optional[str] = Field(None, max_length=512)
    terms_url: Optional[str] = Field(None, max_length=512)
    faq_url: Optional[str] = Field(None, max_length=512)


class ShopSettingsResponse(ShopSettingsBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ShopSettingsPublicResponse(BaseModel):
    """Public response - can be cached and served to frontend"""
    id: int
    shop_name: str
    tagline: Optional[str]
    description: Optional[str]
    owner_name: Optional[str]
    logo_url: Optional[str]
    favicon_url: Optional[str]
    hero_banner_url: Optional[str]
    primary_phone: Optional[str]
    phone_numbers: Optional[str]
    whatsapp: Optional[str]
    email: Optional[str]
    address: Optional[str]
    city: Optional[str]
    state: Optional[str]
    country: Optional[str]
    postal_code: Optional[str]
    business_hours: Optional[str]
    google_maps_url: Optional[str]
    facebook_url: Optional[str]
    instagram_url: Optional[str]
    youtube_url: Optional[str]
    twitter_url: Optional[str]
    linkedin_url: Optional[str]
    footer_text: Optional[str]
    copyright_text: Optional[str]
    privacy_policy_url: Optional[str]
    terms_url: Optional[str]
    faq_url: Optional[str]

    class Config:
        from_attributes = True
