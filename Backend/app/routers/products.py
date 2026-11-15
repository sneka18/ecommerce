from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
import re

from app.database import get_db
from app.core.dependencies import get_current_user, get_optional_current_user, require_role
from app.models.user import User
from app.models.seller import Seller
from app.models.category import Category
from app.models.product import Product
from app.models.review import ProductReview
from app.models.interaction import UserInteraction
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse, ProductListResponse
from app.schemas.category import CategoryResponse, CategoryCreate
from app.schemas.review import ReviewCreate, ReviewResponse

router = APIRouter(tags=["Products & Categories"])


def generate_slug(text: str) -> str:
    """Generate a clean URL slug from title string."""
    clean = re.sub(r'[^a-zA-Z0-9\s-]', '', text).strip().lower()
    return re.sub(r'[\s-]+', '-', clean)


# ---------------------- CATEGORIES ----------------------

@router.get("/categories", response_model=List[CategoryResponse])
def get_categories(db: Session = Depends(get_db)):
    """Retrieve all product categories."""
    return db.query(Category).order_by(Category.name.asc()).all()


@router.post("/categories", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(category_in: CategoryCreate, current_user: User = Depends(require_role("admin")), db: Session = Depends(get_db)):
    """Create a new product category (Admin only)."""
    slug = category_in.slug or generate_slug(category_in.name)
    existing = db.query(Category).filter(or_(Category.name == category_in.name, Category.slug == slug)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Category with this name or slug already exists.")

    new_cat = Category(
        name=category_in.name,
        slug=slug,
        description=category_in.description,
        image_url=category_in.image_url
    )
    db.add(new_cat)
    db.commit()
    db.refresh(new_cat)
    return new_cat


# ---------------------- PRODUCTS ----------------------

@router.get("/products", response_model=ProductListResponse)
def list_products(
    page: int = Query(1, ge=1),
    limit: int = Query(12, ge=1, le=100),
    category_id: Optional[int] = Query(None),
    category_slug: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    min_rating: Optional[float] = Query(None, ge=0, le=5),
    sort_by: Optional[str] = Query("popular"),  # 'popular', 'price_asc', 'price_desc', 'newest', 'rating'
    seller_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """List products with advanced filtering, full-text search, and pagination."""
    query = db.query(Product).filter(Product.is_active == True)

    if category_id:
        query = query.filter(Product.category_id == category_id)
    elif category_slug:
        cat = db.query(Category).filter(Category.slug == category_slug).first()
        if cat:
            query = query.filter(Product.category_id == cat.id)

    if seller_id:
        query = query.filter(Product.seller_id == seller_id)

    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)

    if min_rating is not None:
        query = query.filter(Product.rating >= min_rating)

    if search and search.strip():
        term = f"%{search.strip()}%"
        query = query.filter(
            or_(
                Product.name.ilike(term),
                Product.description.ilike(term),
                Product.ai_description.ilike(term)
            )
        )
        # Log search interaction if user is logged in
        if current_user:
            try:
                # Associate interaction with first matching product or popular product
                first_prod = query.first()
                if first_prod:
                    db.add(UserInteraction(
                        user_id=current_user.id,
                        product_id=first_prod.id,
                        interaction_type="search",
                        rating=3.0
                    ))
                    db.commit()
            except Exception:
                db.rollback()

    # Sorting
    if sort_by == "price_asc":
        query = query.order_by(Product.price.asc())
    elif sort_by == "price_desc":
        query = query.order_by(Product.price.desc())
    elif sort_by == "newest":
        query = query.order_by(Product.created_at.desc())
    elif sort_by == "rating":
        query = query.order_by(Product.rating.desc())
    else:  # popular default
        query = query.order_by(Product.num_reviews.desc(), Product.rating.desc())

    total = query.count()
    offset = (page - 1) * limit
    products = query.offset(offset).limit(limit).all()

    return {"total": total, "items": products}


@router.get("/products/search", response_model=ProductListResponse)
def search_products(
    q: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    limit: int = Query(12, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """Direct search endpoint for products."""
    return list_products(
        page=page,
        limit=limit,
        search=q,
        db=db,
        current_user=current_user
    )


@router.get("/products/{product_id}", response_model=ProductResponse)
def get_product_details(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """Retrieve product details and record 'view' user interaction for recommendation learning."""
    product = db.query(Product).filter(Product.id == product_id, Product.is_active == True).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found or has been deactivated.")

    # Record user browsing view interaction for Machine Learning
    if current_user:
        try:
            interaction = UserInteraction(
                user_id=current_user.id,
                product_id=product.id,
                interaction_type="view",
                rating=3.5
            )
            db.add(interaction)
            db.commit()
        except Exception:
            db.rollback()

    return product


@router.post("/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    product_in: ProductCreate,
    current_user: User = Depends(require_role("seller")),
    db: Session = Depends(get_db)
):
    """Add a new product. Sellers can only add to their own store. Admins can also add."""
    # Retrieve seller profile
    seller = db.query(Seller).filter(Seller.user_id == current_user.id).first()
    if not seller and current_user.role != "admin":
        raise HTTPException(status_code=400, detail="Seller profile not initialized.")

    seller_id = seller.id if seller else 1

    # Verify category exists
    cat = db.query(Category).filter(Category.id == product_in.category_id).first()
    if not cat:
        raise HTTPException(status_code=400, detail="Specified category does not exist.")

    slug_base = generate_slug(product_in.name)
    slug = f"{slug_base}-{int(func.unix_timestamp(func.now()))}"

    new_prod = Product(
        seller_id=seller_id,
        category_id=product_in.category_id,
        name=product_in.name,
        slug=slug,
        price=product_in.price,
        stock=product_in.stock,
        image_url=product_in.image_url,
        description=product_in.description,
        ai_description=product_in.ai_description,
        highlights=product_in.highlights,
        specifications=product_in.specifications,
        is_active=product_in.is_active if product_in.is_active is not None else True,
        rating=5.0,
        num_reviews=0
    )
    db.add(new_prod)
    db.commit()
    db.refresh(new_prod)
    return new_prod


@router.put("/products/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product_in: ProductUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Edit an existing product (Seller owner or Admin)."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found.")

    # Ownership check
    if current_user.role != "admin":
        seller = db.query(Seller).filter(Seller.user_id == current_user.id).first()
        if not seller or product.seller_id != seller.id:
            raise HTTPException(status_code=403, detail="You do not have permission to modify this product.")

    # Apply updates
    update_data = product_in.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(product, field, val)

    db.commit()
    db.refresh(product)
    return product


@router.delete("/products/{product_id}")
def delete_product(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Soft delete or deactivate a product."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found.")

    if current_user.role != "admin":
        seller = db.query(Seller).filter(Seller.user_id == current_user.id).first()
        if not seller or product.seller_id != seller.id:
            raise HTTPException(status_code=403, detail="You do not have permission to delete this product.")

    # Soft delete
    product.is_active = False
    db.commit()
    return {"message": "Product deactivated successfully."}


# ---------------------- REVIEWS ----------------------

@router.get("/products/{product_id}/reviews", response_model=List[ReviewResponse])
def get_product_reviews(product_id: int, db: Session = Depends(get_db)):
    """Fetch customer reviews for a given product."""
    return db.query(ProductReview).filter(ProductReview.product_id == product_id).order_by(ProductReview.created_at.desc()).all()


@router.post("/products/{product_id}/reviews", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
def add_product_review(
    product_id: int,
    review_in: ReviewCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Customer submits a review and rating. Recalculates average rating and records interaction."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found.")

    # Check if user already reviewed
    existing_rev = db.query(ProductReview).filter(
        ProductReview.product_id == product_id,
        ProductReview.user_id == current_user.id
    ).first()

    if existing_rev:
        # Update existing
        existing_rev.rating = review_in.rating
        existing_rev.comment = review_in.comment
        review_obj = existing_rev
    else:
        # Create new review
        review_obj = ProductReview(
            product_id=product_id,
            user_id=current_user.id,
            rating=review_in.rating,
            comment=review_in.comment
        )
        db.add(review_obj)

    db.flush()

    # Recalculate average rating & review count for product
    avg_rating = db.query(func.avg(ProductReview.rating)).filter(ProductReview.product_id == product_id).scalar()
    count_reviews = db.query(func.count(ProductReview.id)).filter(ProductReview.product_id == product_id).scalar()

    product.rating = round(float(avg_rating or review_in.rating), 1)
    product.num_reviews = int(count_reviews or 1)

    # Log ML interaction: rating
    db.add(UserInteraction(
        user_id=current_user.id,
        product_id=product_id,
        interaction_type="rating",
        rating=float(review_in.rating)
    ))

    db.commit()
    db.refresh(review_obj)
    return review_obj

