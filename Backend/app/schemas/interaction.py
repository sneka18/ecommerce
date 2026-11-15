from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class InteractionCreate(BaseModel):
    product_id: int
    interaction_type: str  # 'view', 'search', 'cart', 'purchase', 'rating'
    rating: Optional[float] = None


class InteractionResponse(BaseModel):
    id: int
    user_id: int
    product_id: int
    interaction_type: str
    rating: Optional[float] = None
    timestamp: datetime

    class Config:
        from_attributes = True

