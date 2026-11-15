from typing import List, Optional
from pydantic import BaseModel
from app.schemas.product import ProductResponse


class RecommendationItem(BaseModel):
    product: ProductResponse
    score: float
    reason: str


class RecommendationResponse(BaseModel):
    title: str
    strategy: str  # 'knn_collaborative', 'content_knn', 'cold_start_popular', 'category_affinity'
    recommendations: List[RecommendationItem]

