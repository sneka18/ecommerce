"""
KNN Recommendation Service Module
Loads the serialized Joblib KNN model and provides real-time personalized,
similar-product, and cold-start recommendations.
"""
from pathlib import Path
from typing import List, Dict, Any, Optional
import joblib
import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.product import Product
from app.models.interaction import UserInteraction


class KNNRecommenderService:
    def __init__(self):
        self.model_path = settings.ML_MODELS_DIR / "knn_recommender.joblib"
        self.bundle: Optional[Dict[str, Any]] = None
        self._load_model()

    def _load_model(self):
        """Load trained Joblib model bundle if present."""
        try:
            if self.model_path.exists():
                self.bundle = joblib.load(self.model_path)
                print(f"[KNNRecommenderService] Loaded model bundle from {self.model_path}")
            else:
                print(f"[KNNRecommenderService] Model file not found at {self.model_path}. Will use database fallback.")
        except Exception as e:
            print(f"[KNNRecommenderService] Warning: Could not load model: {e}")
            self.bundle = None

    def get_similar_products(self, product_id: int, db: Session, limit: int = 4) -> List[Dict[str, Any]]:
        """
        Recommend items similar to a given product using Item-KNN feature similarity.
        """
        # If model bundle is available and product is in matrix
        if self.bundle and "item_knn" in self.bundle and product_id in self.bundle["product_ids"]:
            try:
                item_knn = self.bundle["item_knn"]
                item_feature_matrix = self.bundle["item_feature_matrix"]
                pid_idx = self.bundle["product_ids"].index(product_id)

                k = min(limit + 1, len(self.bundle["product_ids"]))
                distances, indices = item_knn.kneighbors(
                    [item_feature_matrix.iloc[pid_idx].values],
                    n_neighbors=k
                )

                similar_items = []
                for dist, neighbor_idx in zip(distances[0][1:], indices[0][1:]):
                    neighbor_pid = self.bundle["product_ids"][neighbor_idx]
                    prod = db.query(Product).filter(Product.id == neighbor_pid, Product.is_active == True).first()
                    if prod:
                        sim_score = round(float(1.0 - dist) * 100, 1)
                        similar_items.append({
                            "product": prod,
                            "score": sim_score,
                            "reason": f"Similar features & category match ({sim_score}% affinity)"
                        })
                if similar_items:
                    return similar_items[:limit]
            except Exception as e:
                print(f"[KNNRecommenderService] Item-KNN error: {e}")

        # Fallback: Query same category products from database
        target = db.query(Product).filter(Product.id == product_id).first()
        cat_id = target.category_id if target else None

        query = db.query(Product).filter(Product.id != product_id, Product.is_active == True)
        if cat_id:
            query = query.filter(Product.category_id == cat_id)

        fallback_prods = query.order_by(Product.rating.desc()).limit(limit).all()
        return [
            {
                "product": p,
                "score": round(p.rating * 20.0, 1),
                "reason": "Top rated in the same category"
            }
            for p in fallback_prods
        ]

    def get_personalized_recommendations(
        self,
        user_id: Optional[int],
        db: Session,
        limit: int = 6
    ) -> Dict[str, Any]:
        """
        Generate personalized recommendations for a user.
        If user has interactions -> User-KNN Collaborative recommendations.
        If new user or guest -> Cold-Start strategy (Popular & Trending).
        """
        # Cold start check
        if not user_id:
            return self._cold_start_recommendations(db, limit, "Trending Products (Guest Visitor)")

        # Check user interaction history in database
        recent_interactions = db.query(UserInteraction).filter(
            UserInteraction.user_id == user_id
        ).order_by(UserInteraction.timestamp.desc()).limit(20).all()

        if not recent_interactions:
            return self._cold_start_recommendations(db, limit, "Recommended for You (Top Rated & Popular)")

        # Attempt User-KNN collaborative recommendations
        interacted_pids = {i.product_id for i in recent_interactions}

        if self.bundle and "user_knn" in self.bundle and "user_item_matrix" in self.bundle:
            try:
                user_item_matrix = self.bundle["user_item_matrix"]
                user_knn = self.bundle["user_knn"]

                # If user exists in matrix or create interaction vector
                if user_id in user_item_matrix.index:
                    u_vec = user_item_matrix.loc[user_id].values.reshape(1, -1)
                else:
                    # Build dynamic interaction vector for this user
                    vec = np.zeros(len(user_item_matrix.columns))
                    weight_map = {"view": 2.0, "search": 2.5, "cart": 4.0, "purchase": 5.0, "rating": 4.5}
                    for interaction in recent_interactions:
                        pid = interaction.product_id
                        if pid in user_item_matrix.columns:
                            col_idx = user_item_matrix.columns.get_loc(pid)
                            score = interaction.rating or weight_map.get(interaction.interaction_type, 3.0)
                            vec[col_idx] = max(vec[col_idx], score)
                    u_vec = vec.reshape(1, -1)

                distances, indices = user_knn.kneighbors(u_vec, n_neighbors=min(5, len(user_item_matrix)))

                scores = {}
                for dist, neighbor_idx in zip(distances[0][1:], indices[0][1:]):
                    sim = 1.0 - dist
                    neighbor_uid = user_item_matrix.index[neighbor_idx]
                    neighbor_ratings = user_item_matrix.loc[neighbor_uid]

                    for pid, rating in neighbor_ratings.items():
                        if pid not in interacted_pids and rating > 0:
                            scores[pid] = scores.get(pid, 0.0) + (sim * rating)

                if scores:
                    sorted_pids = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:limit]
                    recs = []
                    for pid, s in sorted_pids:
                        prod = db.query(Product).filter(Product.id == pid, Product.is_active == True).first()
                        if prod:
                            recs.append({
                                "product": prod,
                                "score": round(float(s), 2),
                                "reason": "Recommended based on similar shopper preferences (KNN Collaborative)"
                            })
                    if recs:
                        return {
                            "title": "Recommended for You",
                            "strategy": "knn_collaborative",
                            "recommendations": recs
                        }
            except Exception as e:
                print(f"[KNNRecommenderService] User-KNN collaborative error: {e}")

        # Secondary personalization: Content similarity to user's most interacted product
        most_recent_prod_id = recent_interactions[0].product_id
        similar = self.get_similar_products(most_recent_prod_id, db, limit=limit)
        filtered = [item for item in similar if item["product"].id not in interacted_pids]

        if filtered:
            return {
                "title": "Based on Your Recent Interests",
                "strategy": "content_knn",
                "recommendations": filtered
            }

        return self._cold_start_recommendations(db, limit, "Popular Items You May Like")

    def _cold_start_recommendations(self, db: Session, limit: int, title: str) -> Dict[str, Any]:
        """Cold-start strategy: returns top rated and popular products."""
        products = db.query(Product).filter(
            Product.is_active == True
        ).order_by(Product.num_reviews.desc(), Product.rating.desc()).limit(limit).all()

        return {
            "title": title,
            "strategy": "cold_start_popular",
            "recommendations": [
                {
                    "product": p,
                    "score": round(p.rating * 20.0, 1),
                    "reason": f"Popular choice with {p.num_reviews} reviews and {p.rating}★ rating"
                }
                for p in products
            ]
        }


recommender_service = KNNRecommenderService()

