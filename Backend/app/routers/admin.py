from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.core.dependencies import require_role
from app.models.user import User
from app.models.seller import Seller
from app.models.product import Product
from app.models.order import Order
from app.schemas.user import UserResponse
from app.schemas.seller import SellerResponse
from app.schemas.product import ProductResponse
from app.schemas.order import OrderResponse, OrderStatusUpdate

router = APIRouter(prefix="/admin", tags=["Administrator Management"])


@router.get("/dashboard")
def get_admin_dashboard(current_user: User = Depends(require_role("admin")), db: Session = Depends(get_db)):
    """Retrieve comprehensive platform-wide analytics for administrator."""
    total_customers = db.query(func.count(User.id)).filter(User.role == "customer").scalar() or 0
    total_sellers = db.query(func.count(Seller.id)).scalar() or 0
    total_products = db.query(func.count(Product.id)).scalar() or 0
    total_orders = db.query(func.count(Order.id)).scalar() or 0
    total_revenue = db.query(func.sum(Order.total_amount)).scalar() or 0.0

    recent_orders = db.query(Order).order_by(Order.created_at.desc()).limit(6).all()
    formatted_recent_orders = [
        {
            "id": o.id,
            "total_amount": float(o.total_amount),
            "status": o.status,
            "customer_name": o.user.full_name if o.user else "User",
            "created_at": o.created_at
        }
        for o in recent_orders
    ]

    recent_users = db.query(User).order_by(User.created_at.desc()).limit(6).all()
    formatted_recent_users = [
        {
            "id": u.id,
            "full_name": u.full_name,
            "email": u.email,
            "role": u.role,
            "is_active": u.is_active,
            "created_at": u.created_at
        }
        for u in recent_users
    ]

    return {
        "total_customers": total_customers,
        "total_sellers": total_sellers,
        "total_products": total_products,
        "total_orders": total_orders,
        "total_revenue": round(float(total_revenue), 2),
        "recent_orders": formatted_recent_orders,
        "recent_users": formatted_recent_users
    }


@router.get("/users", response_model=List[UserResponse])
def get_all_users(
    role: Optional[str] = Query(None),
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """List all registered platform users, optionally filtered by role."""
    query = db.query(User)
    if role:
        query = query.filter(User.role == role)
    return query.order_by(User.created_at.desc()).all()


@router.put("/users/{user_id}/status")
def toggle_user_status(
    user_id: int,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """Toggle activation status of a user account."""
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot deactivate your own administrator account.")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    user.is_active = not user.is_active
    db.commit()
    return {"message": f"User '{user.full_name}' status updated to {'active' if user.is_active else 'inactive'}.", "is_active": user.is_active}


@router.get("/sellers", response_model=List[SellerResponse])
def get_all_sellers(current_user: User = Depends(require_role("admin")), db: Session = Depends(get_db)):
    """List all seller stores on the platform."""
    return db.query(Seller).order_by(Seller.created_at.desc()).all()


@router.get("/products", response_model=List[ProductResponse])
def get_all_admin_products(current_user: User = Depends(require_role("admin")), db: Session = Depends(get_db)):
    """List all products in the database including inactive ones."""
    return db.query(Product).order_by(Product.created_at.desc()).all()


@router.put("/products/{product_id}/status")
def toggle_product_status(
    product_id: int,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """Toggle active state of a product across the platform."""
    prod = db.query(Product).filter(Product.id == product_id).first()
    if not prod:
        raise HTTPException(status_code=404, detail="Product not found.")

    prod.is_active = not prod.is_active
    db.commit()
    return {"message": f"Product '{prod.name}' is now {'active' if prod.is_active else 'inactive'}.", "is_active": prod.is_active}


@router.get("/orders", response_model=List[OrderResponse])
def get_all_admin_orders(current_user: User = Depends(require_role("admin")), db: Session = Depends(get_db)):
    """List all customer orders on the platform."""
    return db.query(Order).order_by(Order.created_at.desc()).all()


@router.put("/orders/{order_id}/status", response_model=OrderResponse)
def update_admin_order_status(
    order_id: int,
    status_update: OrderStatusUpdate,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """Update status of any order on the platform."""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found.")

    allowed_statuses = ["Pending", "Processing", "Shipped", "Delivered", "Cancelled"]
    if status_update.status not in allowed_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {allowed_statuses}")

    order.status = status_update.status
    if status_update.status == "Delivered":
        order.payment_status = "Paid"

    db.commit()
    db.refresh(order)
    return order

