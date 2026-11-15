"""
Dataset Generator for User Interactions
Generates rich, realistic user-product interactions across diverse customer personas.
"""
import pandas as pd
import numpy as np

np.random.seed(42)

# Customer personas and their preferred product IDs
personas = {
    'tech': ([1, 2, 3, 4, 13, 20], [1, 4, 7, 10, 15, 20]),
    'fitness': ([3, 6, 10, 11, 14, 16], [2, 5, 8, 12, 16, 22]),
    'home_coffee': ([8, 9, 15, 18, 11], [3, 6, 9, 13, 17, 23]),
    'fashion': ([5, 6, 7, 17, 3], [11, 14, 18, 21, 24]),
    'stationery': ([12, 19, 2, 9], [19, 25])
}

rows = []
for p_name, (prods, users) in personas.items():
    for u in users:
        # primary products
        for prod in prods:
            # Random interaction type
            itype = str(np.random.choice(['view', 'cart', 'purchase', 'rating'], p=[0.35, 0.25, 0.25, 0.15]))
            weight_map = {'view': 2.5, 'cart': 4.0, 'purchase': 5.0, 'rating': float(np.random.choice([4.0, 4.5, 5.0]))}
            rows.append({
                'user_id': u,
                'product_id': prod,
                'interaction_type': itype,
                'rating': weight_map[itype],
                'timestamp': '2026-10-15 12:00:00'
            })
        # Occasional cross-category exploration
        other_prod = int(np.random.choice([p for p in range(1, 21) if p not in prods]))
        rows.append({
            'user_id': u,
            'product_id': other_prod,
            'interaction_type': 'view',
            'rating': 2.0,
            'timestamp': '2026-10-16 14:30:00'
        })

df = pd.DataFrame(rows).drop_duplicates(subset=['user_id', 'product_id', 'interaction_type'])
df.to_csv('ML/dataset/user_interactions.csv', index=False)
print(f"Successfully generated user_interactions.csv with {len(df)} records across {df['user_id'].nunique()} users.")

