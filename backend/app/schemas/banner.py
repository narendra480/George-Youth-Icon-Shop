from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class BannerBase(BaseModel):
    title: Optional[str] = None
    subtitle: Optional[str] = None
    description: Optional[str] = None
    image_url: str
    mobile_image_url: Optional[str] = None
    link_url: Optional[str] = None
    position: str = "home"
    sort_order: int = 0
    is_active: bool = True
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    background_color: Optional[str] = None
    text_color: Optional[str] = None
    overlay_opacity: Optional[float] = 0.5
    banner_type: Optional[str] = "hero"
    redirect_type: Optional[str] = "url"
    cta_button_1_text: Optional[str] = None
    cta_button_1_url: Optional[str] = None
    cta_button_2_text: Optional[str] = None
    cta_button_2_url: Optional[str] = None
    category_id: Optional[int] = None
    product_id: Optional[int] = None
    collection_id: Optional[int] = None
    is_featured: bool = False

class BannerCreate(BannerBase):
    pass

class BannerUpdate(BaseModel):
    title: Optional[str] = None
    subtitle: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    mobile_image_url: Optional[str] = None
    link_url: Optional[str] = None
    position: Optional[str] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    background_color: Optional[str] = None
    text_color: Optional[str] = None
    overlay_opacity: Optional[float] = None
    banner_type: Optional[str] = None
    redirect_type: Optional[str] = None
    cta_button_1_text: Optional[str] = None
    cta_button_1_url: Optional[str] = None
    cta_button_2_text: Optional[str] = None
    cta_button_2_url: Optional[str] = None
    category_id: Optional[int] = None
    product_id: Optional[int] = None
    collection_id: Optional[int] = None
    is_featured: Optional[bool] = None

class BannerResponse(BannerBase):
    id: int
    view_count: int = 0
    click_count: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True