from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.product import Product
from app.models.cart import Cart, CartItem
from app.models.interaction import UserInteraction
from app.schemas.cart import CartItemCreate, CartItemUpdate, CartResponse

router = APIRouter(prefix="/cart", tags=["Shopping Cart"])


def _format_cart_response(cart: Cart) -> dict:
    total_items = sum(item.quantity for item in cart.items if item.product and item.product.is_active)
    subtotal = sum(float(item.product.price) * item.quantity for item in cart.items if item.product and item.product.is_active)
    return {
        "id": cart.id,
        "user_id": cart.user_id,
        "total_items": total_items,
        "subtotal": round(subtotal, 2),
        "items": [item for item in cart.items if item.product and item.product.is_active]
    }


@router.get("", response_model=CartResponse)
def get_cart(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Retrieve the current user's shopping cart and item details."""
    cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()
    if not cart:
        cart = Cart(user_id=current_user.id)
        db.add(cart)
        db.commit()
        db.refresh(cart)
    return _format_cart_response(cart)


@router.post("", response_model=CartResponse)
def add_to_cart(item_in: CartItemCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Add a product to cart and record 'cart' interaction for ML recommendations."""
    product = db.query(Product).filter(Product.id == item_in.product_id, Product.is_active == True).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found or unavailable.")

    if product.stock < item_in.quantity:
        raise HTTPException(status_code=400, detail=f"Insufficient stock. Only {product.stock} units available.")

    cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()
    if not cart:
        cart = Cart(user_id=current_user.id)
        db.add(cart)
        db.flush()

    existing_item = db.query(CartItem).filter(CartItem.cart_id == cart.id, CartItem.product_id == item_in.product_id).first()
    if existing_item:
        new_qty = existing_item.quantity + item_in.quantity
        if product.stock < new_qty:
            raise HTTPException(status_code=400, detail=f"Cannot add more. Reached available stock limit of {product.stock}.")
        existing_item.quantity = new_qty
    else:
        cart_item = CartItem(
            cart_id=cart.id,
            product_id=item_in.product_id,
            quantity=item_in.quantity
        )
        db.add(cart_item)

    # Record 'cart' interaction for ML model
    try:
        interaction = UserInteraction(
            user_id=current_user.id,
            product_id=product.id,
            interaction_type="cart",
            rating=4.0
        )
        db.add(interaction)
    except Exception:
        pass

    db.commit()
    db.refresh(cart)
    return _format_cart_response(cart)


@router.put("/{cart_item_id}", response_model=CartResponse)
def update_cart_item(cart_item_id: int, item_in: CartItemUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Update quantity of an item in the shopping cart."""
    cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found.")

    cart_item = db.query(CartItem).filter(CartItem.id == cart_item_id, CartItem.cart_id == cart.id).first()
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found.")

    if cart_item.product.stock < item_in.quantity:
        raise HTTPException(status_code=400, detail=f"Insufficient stock. Only {cart_item.product.stock} units available.")

    cart_item.quantity = item_in.quantity
    db.commit()
    db.refresh(cart)
    return _format_cart_response(cart)


@router.delete("/{cart_item_id}", response_model=CartResponse)
def remove_cart_item(cart_item_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Remove a specific item from the shopping cart."""
    cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found.")

    cart_item = db.query(CartItem).filter(CartItem.id == cart_item_id, CartItem.cart_id == cart.id).first()
    if cart_item:
        db.delete(cart_item)
        db.commit()
        db.refresh(cart)

    return _format_cart_response(cart)


@router.delete("", response_model=CartResponse)
def clear_cart(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Clear all items from the current user's cart."""
    cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()
    if cart:
        db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
        db.commit()
        db.refresh(cart)
    return _format_cart_response(cart)

