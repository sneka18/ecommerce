from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.dependencies import get_optional_current_user
from app.models.user import User
from app.schemas.recommendation import RecommendationResponse, RecommendationItem
from app.ml.recommender import recommender_service

router = APIRouter(prefix="/recommendations", tags=["ML Recommendations"])


@router.get("", response_model=RecommendationResponse)
def get_recommendations(
    limit: int = Query(6, ge=1, le=20),
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    """
    Get personalized recommendations using the trained K-Nearest Neighbors (KNN) model.
    Automatically applies cold-start popular products for guest visitors or new users.
    """
    user_id = current_user.id if current_user else None
    return recommender_service.get_personalized_recommendations(user_id=user_id, db=db, limit=limit)


@router.get("/similar/{product_id}", response_model=List[RecommendationItem])
def get_similar_products(
    product_id: int,
    limit: int = Query(4, ge=1, le=10),
    db: Session = Depends(get_db)
):
    """
    Get products similar to a given product using Item-KNN multi-feature cosine similarity.
    """
    return recommender_service.get_similar_products(product_id=product_id, db=db, limit=limit)


@router.get("/popular", response_model=RecommendationResponse)
def get_popular_products(
    limit: int = Query(6, ge=1, le=20),
    db: Session = Depends(get_db)
):
    """
    Cold-start popular and trending products.
    """
    return recommender_service._cold_start_recommendations(db=db, limit=limit, title="Trending & Bestselling Products")

