"""
Model Training Module for KNN Recommender
Trains K-Nearest Neighbors recommendation models on user interactions and product features.
Saves the artifact bundle with Joblib.
"""
from pathlib import Path
import joblib
import pandas as pd
import numpy as np
from sklearn.neighbors import NearestNeighbors
from preprocess import RecommenderPreprocessor


def train_knn_models(save_model: bool = True):
    print("=" * 60)
    print("Training K-Nearest Neighbors (KNN) Recommender System")
    print("=" * 60)

    preprocessor = RecommenderPreprocessor()
    product_df, interactions_df = preprocessor.load_data()
    print(f" Loaded {len(product_df)} products and {len(interactions_df)} user interactions.")

    # 1. Build Matrices
    user_item_matrix = preprocessor.build_user_item_matrix()
    item_feature_matrix = preprocessor.build_item_feature_matrix()
    print(f" User-Item Matrix Shape:    {user_item_matrix.shape} (Users x Products)")
    print(f" Item-Feature Matrix Shape: {item_feature_matrix.shape} (Products x Features)")

    # 2. Train Item-Based KNN Model (Cosine Distance)
    # Allows finding similar products based on multi-attribute feature vectors
    n_item_neighbors = min(6, len(item_feature_matrix))
    item_knn = NearestNeighbors(n_neighbors=n_item_neighbors, metric="cosine", algorithm="brute")
    item_knn.fit(item_feature_matrix.values)
    print(f" Fitted Item-KNN Model with metric='cosine', k={n_item_neighbors}")

    # 3. Train User-Based Collaborative KNN Model
    n_user_neighbors = min(5, len(user_item_matrix))
    user_knn = NearestNeighbors(n_neighbors=n_user_neighbors, metric="cosine", algorithm="brute")
    user_knn.fit(user_item_matrix.values)
    print(f" Fitted User-KNN Model with metric='cosine', k={n_user_neighbors}")

    # 4. Save Artifact Bundle
    bundle = {
        "item_knn": item_knn,
        "user_knn": user_knn,
        "user_item_matrix": user_item_matrix,
        "item_feature_matrix": item_feature_matrix,
        "product_df": product_df,
        "category_encoder": preprocessor.category_encoder,
        "scaler": preprocessor.scaler,
        "product_ids": list(item_feature_matrix.index)
    }

    if save_model:
        models_dir = Path(__file__).resolve().parent.parent / "models"
        models_dir.mkdir(parents=True, exist_ok=True)
        model_path = models_dir / "knn_recommender.joblib"
        joblib.dump(bundle, model_path)
        print(f" Model bundle successfully saved to: {model_path}")

    # Quick test demonstration
    print("\n[Test Recommendation Check]")
    sample_pid = bundle["product_ids"][0]
    prod_row = product_df[product_df["product_id"] == sample_pid].iloc[0]
    print(f"Query Product: #{sample_pid} - {prod_row['name']} ({prod_row['category_name']})")

    idx = bundle["product_ids"].index(sample_pid)
    distances, indices = item_knn.kneighbors([item_feature_matrix.iloc[idx].values], n_neighbors=4)

    print("Top Similar Products:")
    for dist, neighbor_idx in zip(distances[0][1:], indices[0][1:]):
        neighbor_pid = bundle["product_ids"][neighbor_idx]
        n_row = product_df[product_df["product_id"] == neighbor_pid].iloc[0]
        similarity = round((1 - dist) * 100, 1)
        print(f"  --> #{neighbor_pid}: {n_row['name']} | Category: {n_row['category_name']} | Similarity: {similarity}%")

    print("=" * 60)
    return bundle


if __name__ == "__main__":
    train_knn_models(save_model=True)

