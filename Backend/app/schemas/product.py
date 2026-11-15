from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from app.schemas.category import CategoryResponse
from app.schemas.seller import SellerResponse


class ProductBase(BaseModel):
    name: str
    category_id: int
    price: float = Field(..., gt=0)
    stock: int = Field(..., ge=0)
    image_url: Optional[str] = None
    description: Optional[str] = None
    ai_description: Optional[str] = None
    highlights: Optional[str] = None
    specifications: Optional[str] = None
    is_active: Optional[bool] = True


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    category_id: Optional[int] = None
    price: Optional[float] = Field(None, gt=0)
    stock: Optional[int] = Field(None, ge=0)
    image_url: Optional[str] = None
    description: Optional[str] = None
    ai_description: Optional[str] = None
    highlights: Optional[str] = None
    specifications: Optional[str] = None
    is_active: Optional[bool] = None


class ProductResponse(BaseModel):
    id: int
    seller_id: int
    category_id: int
    name: str
    slug: str
    price: float
    stock: int
    image_url: Optional[str] = None
    description: Optional[str] = None
    ai_description: Optional[str] = None
    highlights: Optional[str] = None
    specifications: Optional[str] = None
    rating: float
    num_reviews: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    category: Optional[CategoryResponse] = None
    seller: Optional[SellerResponse] = None

    class Config:
        from_attributes = True


class ProductListResponse(BaseModel):
    total: int
    items: List[ProductResponse]

