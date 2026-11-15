from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.core.dependencies import require_role
from app.models.user import User
from app.models.seller import Seller
from app.models.product import Product
from app.models.order import Order, OrderItem
from app.schemas.product import ProductResponse
from app.schemas.order import OrderResponse, OrderStatusUpdate

router = APIRouter(prefix="/seller", tags=["Seller Management"])


@router.get("/dashboard")
def get_seller_dashboard(current_user: User = Depends(require_role("seller")), db: Session = Depends(get_db)):
    """Retrieve summary statistics and recent orders for seller dashboard."""
    seller = db.query(Seller).filter(Seller.user_id == current_user.id).first()
    if not seller:
        raise HTTPException(status_code=400, detail="Seller profile not initialized.")

    # Total products listed by seller
    total_products = db.query(func.count(Product.id)).filter(Product.seller_id == seller.id, Product.is_active == True).scalar() or 0

    # Low stock items (< 10)
    low_stock_count = db.query(func.count(Product.id)).filter(
        Product.seller_id == seller.id,
        Product.stock < 10,
        Product.is_active == True
    ).scalar() or 0

    # Orders containing seller items
    seller_order_items = db.query(OrderItem).filter(OrderItem.seller_id == seller.id).all()
    total_seller_items_sold = sum(item.quantity for item in seller_order_items)
    total_revenue = sum(float(item.price) * item.quantity for item in seller_order_items)

    unique_order_ids = list(set(item.order_id for item in seller_order_items))
    total_orders = len(unique_order_ids)

    # Recent 5 orders
    recent_orders = []
    if unique_order_ids:
        orders = db.query(Order).filter(Order.id.in_(unique_order_ids)).order_by(Order.created_at.desc()).limit(5).all()
        for o in orders:
            recent_orders.append({
                "id": o.id,
                "total_amount": float(o.total_amount),
                "status": o.status,
                "customer_name": o.user.full_name if o.user else "Customer",
                "created_at": o.created_at
            })

    return {
        "store_name": seller.store_name,
        "total_revenue": round(total_revenue, 2),
        "total_orders": total_orders,
        "total_products": total_products,
        "total_units_sold": total_seller_items_sold,
        "low_stock_alerts": low_stock_count,
        "recent_orders": recent_orders
    }


@router.get("/products", response_model=List[ProductResponse])
def get_seller_products(current_user: User = Depends(require_role("seller")), db: Session = Depends(get_db)):
    """Retrieve all products created by the current seller."""
    seller = db.query(Seller).filter(Seller.user_id == current_user.id).first()
    if not seller:
        raise HTTPException(status_code=400, detail="Seller profile not found.")
    return db.query(Product).filter(Product.seller_id == seller.id).order_by(Product.created_at.desc()).all()


@router.get("/orders", response_model=List[OrderResponse])
def get_seller_orders(current_user: User = Depends(require_role("seller")), db: Session = Depends(get_db)):
    """Retrieve customer orders containing products from this seller."""
    seller = db.query(Seller).filter(Seller.user_id == current_user.id).first()
    if not seller:
        raise HTTPException(status_code=400, detail="Seller profile not found.")

    order_ids = db.query(OrderItem.order_id).filter(OrderItem.seller_id == seller.id).distinct().all()
    ids = [oid[0] for oid in order_ids]
    if not ids:
        return []

    return db.query(Order).filter(Order.id.in_(ids)).order_by(Order.created_at.desc()).all()


@router.put("/orders/{order_id}/status", response_model=OrderResponse)
def update_order_status(
    order_id: int,
    status_update: OrderStatusUpdate,
    current_user: User = Depends(require_role("seller")),
    db: Session = Depends(get_db)
):
    """Update delivery/fulfillment status of an order."""
    seller = db.query(Seller).filter(Seller.user_id == current_user.id).first()
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found.")

    # Validate seller has items in this order (or admin)
    has_items = db.query(OrderItem).filter(OrderItem.order_id == order.id, OrderItem.seller_id == seller.id).first()
    if not has_items and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Order does not contain products from your store.")

    allowed_statuses = ["Pending", "Processing", "Shipped", "Delivered", "Cancelled"]
    if status_update.status not in allowed_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {allowed_statuses}")

    order.status = status_update.status
    if status_update.status == "Delivered":
        order.payment_status = "Paid"

    db.commit()
    db.refresh(order)
    return order

