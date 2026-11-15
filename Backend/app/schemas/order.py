from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from app.schemas.product import ProductResponse


class OrderCreate(BaseModel):
    shipping_address: str
    payment_method: Optional[str] = "Cash on Delivery"


class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    seller_id: int
    quantity: int
    price: float
    product: Optional[ProductResponse] = None

    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    id: int
    user_id: int
    total_amount: float
    shipping_address: str
    payment_method: str
    payment_status: str
    status: str
    created_at: datetime
    updated_at: datetime
    items: List[OrderItemResponse]

    class Config:
        from_attributes = True


class OrderStatusUpdate(BaseModel):
    status: str  # 'Pending', 'Processing', 'Shipped', 'Delivered', 'Cancelled'

