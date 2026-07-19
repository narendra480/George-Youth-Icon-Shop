from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class AddressBase(BaseModel):
    name: str
    mobile: str
    alternate_mobile: Optional[str] = None
    house_flat: str
    street: str
    landmark: Optional[str] = None
    area: Optional[str] = None
    district: Optional[str] = None
    city: str
    state: str
    country: Optional[str] = "India"
    pincode: str
    address_type: str = "home"
    is_default: bool = False
    gst_number: Optional[str] = None


class AddressCreate(AddressBase):
    pass


class AddressUpdate(BaseModel):
    name: Optional[str] = None
    mobile: Optional[str] = None
    alternate_mobile: Optional[str] = None
    house_flat: Optional[str] = None
    street: Optional[str] = None
    landmark: Optional[str] = None
    area: Optional[str] = None
    district: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    pincode: Optional[str] = None
    address_type: Optional[str] = None
    is_default: Optional[bool] = None
    gst_number: Optional[str] = None


class AddressResponse(AddressBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True