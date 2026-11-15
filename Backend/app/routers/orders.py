from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.product import Product
from app.models.cart import Cart, CartItem
from app.models.order import Order, OrderItem
from app.models.interaction import UserInteraction
from app.schemas.order import OrderCreate, OrderResponse

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def place_order(order_in: OrderCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Checkout current cart, deduct stock, log purchase interactions, and create an order."""
    cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()
    if not cart or not cart.items:
        raise HTTPException(status_code=400, detail="Cannot place order: your shopping cart is empty.")

    # Validate stock for all cart items first
    total_amount = 0.0
    items_to_order = []

    for item in cart.items:
        prod = item.product
        if not prod or not prod.is_active:
            raise HTTPException(status_code=400, detail=f"Product '{prod.name if prod else 'Unknown'}' is currently unavailable.")
        if prod.stock < item.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot checkout: insufficient stock for '{prod.name}'. Only {prod.stock} units remaining."
            )
        total_amount += float(prod.price) * item.quantity
        items_to_order.append((prod, item.quantity))

    # Create Order
    new_order = Order(
        user_id=current_user.id,
        total_amount=round(total_amount, 2),
        shipping_address=order_in.shipping_address,
        payment_method=order_in.payment_method or "Cash on Delivery",
        payment_status="Paid" if order_in.payment_method != "Cash on Delivery" else "Pending",
        status="Pending"
    )
    db.add(new_order)
    db.flush()

    # Deduct stock, create OrderItems, and log 'purchase' interactions for ML
    for prod, qty in items_to_order:
        prod.stock -= qty
        order_item = OrderItem(
            order_id=new_order.id,
            product_id=prod.id,
            seller_id=prod.seller_id,
            quantity=qty,
            price=prod.price
        )
        db.add(order_item)

        # Log ML interaction: purchase (strongest positive signal: 5.0)
        try:
            interaction = UserInteraction(
                user_id=current_user.id,
                product_id=prod.id,
                interaction_type="purchase",
                rating=5.0
            )
            db.add(interaction)
        except Exception:
            pass

    # Clear user's cart
    db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()

    db.commit()
    db.refresh(new_order)
    return new_order


@router.get("", response_model=List[OrderResponse])
def get_user_orders(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Retrieve all orders placed by the current user, sorted newest first."""
    return db.query(Order).filter(Order.user_id == current_user.id).order_by(Order.created_at.desc()).all()


@router.get("/{order_id}", response_model=OrderResponse)
def get_order_details(order_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Retrieve details for a specific order with ownership verification."""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found.")

    if order.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="You do not have permission to view this order.")

    return order

