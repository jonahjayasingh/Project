from flask import Blueprint, render_template, request, session
from models import Product, Category, User, UserType, SellerProfile, SellerStatus, db
from sqlalchemy import or_

routes = Blueprint('product', __name__)


@routes.route('/products')
def list_products():
    """List all products with advanced filtering and pagination"""
    page = request.args.get('page', 1, type=int)
    category_slug = request.args.get('category')
    search_query = request.args.get('q', '').strip()
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    min_rating = request.args.get('rating', type=int)
    in_stock = request.args.get('in_stock', type=bool, default=True)
    
    # Start query
    from models import ProductVariant, Review
    query = Product.query.join(User, Product.seller_id == User.id).outerjoin(
        SellerProfile, User.id == SellerProfile.user_id
    ).filter(
        SellerProfile.status == SellerStatus.ACTIVE
    )
    
    if in_stock:
        query = query.join(ProductVariant).filter(ProductVariant.stock > 0).group_by(Product.id)
    
    # Exclude seller's own products
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user and user.user_type == UserType.SELLER:
            query = query.filter(Product.seller_id != session['user_id'])
    
    if category_slug:
        category = Category.query.filter_by(slug=category_slug).first()
        if category:
            query = query.filter(Product.category_id == category.id)
    
    if search_query:
        query = query.filter(
            or_(
                Product.name.contains(search_query),
                Product.description.contains(search_query)
            )
        )
    
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)

    # Note: Rating filter would ideally use a subquery or join with Review and group_by
    # For now, keeping it simple as per doctrine while ensuring correctness
    
    pagination = query.order_by(Product.created_at.desc()).paginate(page=page, per_page=12)
    categories = Category.query.all()
    
    return render_template(
        'products/list.html',
        products=pagination.items,
        pagination=pagination,
        categories=categories,
        current_category=category_slug,
        search_query=search_query,
        min_price=min_price,
        max_price=max_price,
        min_rating=min_rating
    )


@routes.route('/products/<int:product_id>')
def product_detail(product_id):
    """Display single product details"""
    from models import Review, Order, OrderItem
    
    product = Product.query.get_or_404(product_id)
    
    # Get related products from same category
    related_products = []
    if product.category_id:
        related_products = Product.query.filter(
            Product.category_id == product.category_id,
            Product.id != product.id,
            Product.quantity > 0
        ).limit(4).all()
    
    # Get reviews for this product
    reviews = Review.query.filter_by(product_id=product_id).order_by(Review.created_at.desc()).all()
    
    # Calculate average rating
    avg_rating = 0
    if reviews:
        avg_rating = sum(r.rating for r in reviews) / len(reviews)
    
    # Check if current user can review (logged in and purchased)
    can_review = False
    has_reviewed = False
    if 'user_id' in session:
        user_id = session['user_id']
        
        # Check if user purchased this product
        from models import ProductVariant
        has_purchased = db.session.query(OrderItem).join(Order).join(ProductVariant).filter(
            Order.user_id == user_id,
            ProductVariant.product_id == product_id
        ).first()
        
        # Check if user already reviewed
        has_reviewed = Review.query.filter_by(
            user_id=user_id,
            product_id=product_id
        ).first() is not None
        
        can_review = has_purchased and not has_reviewed
    
    return render_template(
        'products/detail.html',
        product=product,
        related_products=related_products,
        reviews=reviews,
        avg_rating=avg_rating,
        review_count=len(reviews),
        can_review=can_review,
        has_reviewed=has_reviewed
    )


@routes.route('/products/category/<slug>')
def products_by_category(slug):
    """List products by category"""
    category = Category.query.filter_by(slug=slug).first_or_404()
    products = Product.query.filter_by(category_id=category.id).filter(
        Product.quantity > 0
    ).order_by(Product.created_at.desc()).all()
    
    categories = Category.query.all()
    
    return render_template(
        'products/list.html',
        products=products,
        categories=categories,
        current_category=slug,
        category_name=category.name
    )
