from typing import List, Optional
from pydantic import BaseModel


class AIDescriptionRequest(BaseModel):
    product_name: str
    category: str
    price: float
    features: Optional[str] = None
    specifications: Optional[str] = None
    target_audience: Optional[str] = None


class AIHighlightRequest(BaseModel):
    product_name: str
    category: str
    description: Optional[str] = None


class AIShoppingInsightsRequest(BaseModel):
    category: Optional[str] = None
    viewed_products: Optional[List[str]] = None
    interests: Optional[List[str]] = None


class AIResponse(BaseModel):
    success: bool
    data: Optional[dict] = None
    message: Optional[str] = None

