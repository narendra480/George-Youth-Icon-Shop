from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class NotificationBase(BaseModel):
    title: str
    message: str
    type: str = "system"
    link_url: Optional[str] = None


class NotificationResponse(NotificationBase):
    id: int
    user_id: int
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True


class NotificationUpdate(BaseModel):
    is_read: Optional[bool] = None


class UserActivityResponse(BaseModel):
    id: int
    user_id: int
    activity_type: str
    description: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True