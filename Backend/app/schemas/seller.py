from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr


class SellerBase(BaseModel):
    store_name: str
    store_description: Optional[str] = None
    business_email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None


class SellerCreate(SellerBase):
    pass


class SellerUpdate(BaseModel):
    store_name: Optional[str] = None
    store_description: Optional[str] = None
    business_email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None


class SellerResponse(SellerBase):
    id: int
    user_id: int
    is_approved: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

