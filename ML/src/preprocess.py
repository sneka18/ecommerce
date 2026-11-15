"""
Data Preprocessing Module for Recommendation System
Handles data cleaning, normalization, categorical encoding, and matrix construction.
"""
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder


class RecommenderPreprocessor:
    def __init__(self, data_dir: Path = None):
        if data_dir is None:
            data_dir = Path(__file__).resolve().parent.parent / "dataset"
        self.data_dir = data_dir
        self.scaler = MinMaxScaler()
        self.category_encoder = OneHotEncoder(sparse_output=False, handle_unknown="ignore")
        self.product_df = None
        self.interactions_df = None

    def load_data(self):
        """Load datasets from disk with validation."""
        prod_path = self.data_dir / "products.csv"
        inter_path = self.data_dir / "user_interactions.csv"

        if not prod_path.exists():
            raise FileNotFoundError(f"Missing products dataset at {prod_path}")
        if not inter_path.exists():
            raise FileNotFoundError(f"Missing interactions dataset at {inter_path}")

        self.product_df = pd.read_csv(prod_path)
        self.interactions_df = pd.read_csv(inter_path)

        # Handle missing values
        self.product_df["price"] = self.product_df["price"].fillna(self.product_df["price"].median())
        self.product_df["rating"] = self.product_df["rating"].fillna(4.0)
        self.product_df["num_reviews"] = self.product_df["num_reviews"].fillna(0)
        self.interactions_df["rating"] = self.interactions_df["rating"].fillna(3.0)

        return self.product_df, self.interactions_df

    def build_user_item_matrix(self):
        """Construct user-item matrix where values represent user affinity for products."""
        if self.interactions_df is None:
            self.load_data()

        # Aggregate max interaction score if multiple interactions exist for same user-product
        user_item = self.interactions_df.pivot_table(
            index="user_id",
            columns="product_id",
            values="rating",
            aggfunc="max",
            fill_value=0.0
        )
        return user_item

    def build_item_feature_matrix(self):
        """
        Construct multi-faceted product feature matrix combining:
        - One-hot encoded category
        - Scaled price
        - Scaled rating
        - Log-transformed popularity (reviews count)
        """
        if self.product_df is None:
            self.load_data()

        df = self.product_df.copy()

        # 1. One-hot encode category
        cat_encoded = self.category_encoder.fit_transform(df[["category_name"]])
        cat_cols = [f"cat_{c}" for c in self.category_encoder.categories_[0]]
        cat_df = pd.DataFrame(cat_encoded, columns=cat_cols, index=df.index)

        # 2. Numerical feature scaling
        df["log_reviews"] = np.log1p(df["num_reviews"])
        num_features = df[["price", "rating", "log_reviews"]]
        scaled_nums = self.scaler.fit_transform(num_features)
        num_df = pd.DataFrame(scaled_nums, columns=["scaled_price", "scaled_rating", "scaled_popularity"], index=df.index)

        # Combine into complete item feature matrix
        feature_matrix = pd.concat([df[["product_id"]], cat_df, num_df], axis=1)
        feature_matrix.set_index("product_id", inplace=True)

        return feature_matrix

