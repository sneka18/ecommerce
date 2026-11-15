"""
Recommendation Model Evaluation Module
Calculates Precision@K, Recall@K, Hit Rate@K, and Catalog Coverage on held-out test data.
"""
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.neighbors import NearestNeighbors
from preprocess import RecommenderPreprocessor


def evaluate_recommendations(k_values=[3, 5, 10]):
    print("=" * 60)
    print("Evaluating KNN Recommendation System Quality")
    print("=" * 60)

    preprocessor = RecommenderPreprocessor()
    product_df, interactions_df = preprocessor.load_data()
    all_product_ids = set(product_df["product_id"])

    # Train / Test split by user: for each user, keep 80% interactions for train, 20% for test
    np.random.seed(42)
    train_rows = []
    test_rows = []

    for user_id, user_group in interactions_df.groupby("user_id"):
        if len(user_group) < 3:
            train_rows.append(user_group)
            continue
        shuffled = user_group.sample(frac=1.0, random_state=42)
        n_test = max(1, int(len(shuffled) * 0.25))
        test_rows.append(shuffled.iloc[:n_test])
        train_rows.append(shuffled.iloc[n_test:])

    train_df = pd.concat(train_rows).reset_index(drop=True)
    test_df = pd.concat(test_rows).reset_index(drop=True)

    print(f" Train Interactions: {len(train_df)}")
    print(f" Test Interactions:  {len(test_df)} across {test_df['user_id'].nunique()} users")

    # Build train user-item matrix
    train_matrix = train_df.pivot_table(
        index="user_id",
        columns="product_id",
        values="rating",
        aggfunc="max",
        fill_value=0.0
    )

    # Reindex columns to include all catalog products
    for pid in all_product_ids:
        if pid not in train_matrix.columns:
            train_matrix[pid] = 0.0
    train_matrix = train_matrix[sorted(train_matrix.columns)]

    # Fit collaborative KNN on train matrix
    n_neighbors = min(5, len(train_matrix))
    user_knn = NearestNeighbors(n_neighbors=n_neighbors, metric="cosine", algorithm="brute")
    user_knn.fit(train_matrix.values)

    # Collect ground-truth test items per user
    ground_truth = test_df.groupby("user_id")["product_id"].apply(set).to_dict()

    results = {}
    for k in k_values:
        precisions = []
        recalls = []
        hits = []
        recommended_all = set()

        for user_id, true_items in ground_truth.items():
            if user_id not in train_matrix.index:
                continue

            user_vector = train_matrix.loc[user_id].values.reshape(1, -1)
            distances, indices = user_knn.kneighbors(user_vector, n_neighbors=n_neighbors)

            # Aggregate neighbor ratings excluding items the user already interacted with in training
            already_interacted = set(train_df[train_df["user_id"] == user_id]["product_id"])
            scores = {}

            for dist, neighbor_idx in zip(distances[0][1:], indices[0][1:]):
                sim = 1.0 - dist
                neighbor_uid = train_matrix.index[neighbor_idx]
                neighbor_ratings = train_matrix.loc[neighbor_uid]

                for pid, rating in neighbor_ratings.items():
                    if pid not in already_interacted and rating > 0:
                        scores[pid] = scores.get(pid, 0.0) + (sim * rating)

            # Sort top K
            sorted_recs = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:k]
            rec_items = [pid for pid, _ in sorted_recs]

            # If collaborative has fewer than K, fallback to popular un-interacted products
            if len(rec_items) < k:
                popular = [pid for pid in all_product_ids if pid not in already_interacted and pid not in rec_items]
                rec_items.extend(popular[:k - len(rec_items)])

            recommended_all.update(rec_items)

            # Calculate metrics for this user
            intersection = set(rec_items).intersection(true_items)
            precisions.append(len(intersection) / float(k))
            recalls.append(len(intersection) / float(len(true_items)) if len(true_items) > 0 else 0.0)
            hits.append(1.0 if len(intersection) > 0 else 0.0)

        mean_precision = float(np.mean(precisions))
        mean_recall = float(np.mean(recalls))
        mean_hit = float(np.mean(hits))
        coverage = (len(recommended_all) / float(len(all_product_ids))) * 100.0

        results[k] = {
            "Precision@K": round(mean_precision, 4),
            "Recall@K": round(mean_recall, 4),
            "Hit Rate@K": round(mean_hit, 4),
            "Catalog Coverage (%)": round(coverage, 2)
        }

    print("\n" + "=" * 60)
    print("EVALUATION RESULTS SUMMARY (KNN Collaborative Recommender):")
    print("=" * 60)
    print(f"{'Metric':<25} | " + " | ".join([f"K={k:<6}" for k in k_values]))
    print("-" * 60)
    for metric_name in ["Precision@K", "Recall@K", "Hit Rate@K", "Catalog Coverage (%)"]:
        row = f"{metric_name:<25} | "
        row += " | ".join([f"{results[k][metric_name]:<8}" for k in k_values])
        print(row)
    print("=" * 60)

    return results


if __name__ == "__main__":
    evaluate_recommendations()

