from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.security import verify_password, hash_password, create_access_token
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.seller import Seller
from app.models.cart import Cart
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token, UserUpdate

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    """Register a new customer or seller."""
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email address already exists."
        )

    role = user_in.role.lower() if user_in.role else "customer"
    if role not in ("customer", "seller"):
        role = "customer"

    # Create new user
    new_user = User(
        email=user_in.email,
        password_hash=hash_password(user_in.password),
        full_name=user_in.full_name,
        phone=user_in.phone,
        role=role,
        is_active=True
    )
    db.add(new_user)
    db.flush()

    # If registering as customer, automatically create a shopping cart
    if role == "customer":
        new_cart = Cart(user_id=new_user.id)
        db.add(new_cart)

    # If registering as seller, create seller profile
    elif role == "seller":
        store_title = user_in.store_name if user_in.store_name else f"{user_in.full_name}'s Store"
        new_seller = Seller(
            user_id=new_user.id,
            store_name=store_title,
            store_description="Welcome to my official store!",
            business_email=user_in.email,
            phone=user_in.phone,
            is_approved=True
        )
        db.add(new_seller)

    db.commit()
    db.refresh(new_user)

    # Issue JWT token
    access_token = create_access_token(data={"user_id": new_user.id, "email": new_user.email, "role": new_user.role})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": new_user
    }


@router.post("/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Authenticate with email and password and receive a JWT token."""
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This user account has been deactivated. Please contact support."
        )

    access_token = create_access_token(data={"user_id": user.id, "email": user.email, "role": user.role})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Retrieve the currently logged-in user profile."""
    return current_user


@router.put("/profile", response_model=UserResponse)
def update_profile(user_update: UserUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Update current user profile information."""
    if user_update.full_name is not None:
        current_user.full_name = user_update.full_name
    if user_update.phone is not None:
        current_user.phone = user_update.phone
    if user_update.password:
        current_user.password_hash = hash_password(user_update.password)

    db.commit()
    db.refresh(current_user)
    return current_user

