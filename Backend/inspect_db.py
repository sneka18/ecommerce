"""
Database Inspector Script
Displays a quick summary of all tables and sample records in ai_ecommerce_db.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.database import SessionLocal
from app.models.user import User
from app.models.seller import Seller
from app.models.category import Category
from app.models.product import Product
from app.models.order import Order
from app.models.interaction import UserInteraction
from app.models.cart import CartItem

db = SessionLocal()

print("=" * 70)
print("       MYSQL DATABASE INSPECTOR (ai_ecommerce_db)")
print("=" * 70)

try:
    total_users = db.query(User).count()
    total_sellers = db.query(Seller).count()
    total_categories = db.query(Category).count()
    total_products = db.query(Product).count()
    total_orders = db.query(Order).count()
    total_interactions = db.query(UserInteraction).count()

    print(f"\n📊 TABLE COUNTS:")
    print(f"  • users:             {total_users} records")
    print(f"  • sellers:           {total_sellers} records")
    print(f"  • categories:        {total_categories} records")
    print(f"  • products:          {total_products} records")
    print(f"  • orders:            {total_orders} records")
    print(f"  • user_interactions: {total_interactions} records")

    print("\n" + "-" * 70)
    print("👤 SAMPLE USERS (TABLE: users):")
    for u in db.query(User).limit(5).all():
        print(f"  [ID: {u.id}] {u.full_name:<20} | Role: {u.role:<10} | Email: {u.email}")

    print("\n" + "-" * 70)
    print("📦 SAMPLE PRODUCTS (TABLE: products):")
    for p in db.query(Product).limit(5).all():
        cat_name = p.category.name if p.category else 'N/A'
        print(f"  [ID: {p.id:2d}] ${float(p.price):<7.2f} | Stock: {p.stock:3d} | Rating: {p.rating}★ | {p.name[:35]} ({cat_name})")

    print("\n" + "-" * 70)
    print("🛍️ SAMPLE ORDERS (TABLE: orders):")
    orders = db.query(Order).limit(5).all()
    if orders:
        for o in orders:
            cust = o.user.full_name if o.user else "User"
            print(f"  [Order #{o.id}] Customer: {cust:<15} | Total: ${float(o.total_amount):<7.2f} | Status: {o.status}")
    else:
        print("  (No orders placed yet)")

    print("\n" + "-" * 70)
    print("🤖 SAMPLE ML INTERACTIONS (TABLE: user_interactions):")
    for i in db.query(UserInteraction).limit(5).all():
        print(f"  [User #{i.user_id} -> Product #{i.product_id}] Action: {i.interaction_type:<10} | Score: {i.rating}")

    print("\n" + "=" * 70)
except Exception as e:
    print(f"Error reading database: {e}")
finally:
    db.close()

