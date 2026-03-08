from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import User, SellerProfile, SellerStatus, Category, Product, db
from utils.auth import admin_required
import re

routes = Blueprint('admin', __name__)


@routes.route('/dashboard')
@admin_required
def dashboard():
    """Admin dashboard with analytics overview"""
    from models import Order, OrderStatus, Coupon, ReturnRequest
    
    # Statistics
    total_users = User.query.count()
    total_sellers = SellerProfile.query.count()
    active_sellers = SellerProfile.query.filter_by(status=SellerStatus.ACTIVE).count()
    
    # Financials
    total_revenue = db.session.query(db.func.sum(Order.final_amount)).filter(Order.status == OrderStatus.PAID).scalar() or 0
    total_orders = Order.query.count()
    paid_orders = Order.query.filter_by(status=OrderStatus.PAID).count()
    
    # Metrics
    pending_returns = ReturnRequest.query.filter_by(status="pending").count()
    active_coupons = Coupon.query.filter_by(is_active=True).count()
    
    return render_template(
        'admin/dashboard.html',
        total_users=total_users,
        total_sellers=total_sellers,
        active_sellers=active_sellers,
        total_revenue=total_revenue,
        total_orders=total_orders,
        paid_orders=paid_orders,
        pending_returns=pending_returns,
        active_coupons=active_coupons
    )


# --- Coupon Management ---

@routes.route('/coupons')
@admin_required
def manage_coupons():
    from models import Coupon
    coupons = Coupon.query.order_by(Coupon.created_at.desc()).all()
    return render_template('admin/coupons.html', coupons=coupons)

@routes.route('/coupons/add', methods=['GET', 'POST'])
@admin_required
def add_coupon():
    from models import Coupon, DiscountType
    if request.method == 'POST':
        coupon = Coupon(
            code=request.form['code'].upper(),
            discount_type=DiscountType(request.form['discount_type']),
            discount_value=float(request.form['discount_value']),
            min_cart_value=float(request.form.get('min_cart_value', 0)),
            usage_limit=int(request.form.get('usage_limit')) if request.form.get('usage_limit') else None,
            is_active=True
        )
        db.session.add(coupon)
        db.session.commit()
        flash('Coupon created!', 'success')
        return redirect(url_for('admin.manage_coupons'))
    return render_template('admin/coupon_form.html')


# --- Return Management ---

@routes.route('/returns')
@admin_required
def manage_returns():
    from models import ReturnRequest
    returns = ReturnRequest.query.order_by(ReturnRequest.created_at.desc()).all()
    return render_template('admin/returns.html', returns=returns)

@routes.route('/returns/<int:return_id>/process', methods=['POST'])
@admin_required
def process_return(return_id):
    from models import ReturnRequest, ReturnStatus, OrderStatus
    ret = ReturnRequest.query.get_or_404(return_id)
    action = request.form.get('action') # approve/reject
    
    if action == 'approve':
        ret.status = ReturnStatus.APPROVED
        ret.order.status = OrderStatus.RETURNED
        flash('Return approved.', 'success')
    else:
        ret.status = ReturnStatus.REJECTED
        flash('Return rejected.', 'info')
        
    ret.admin_comment = request.form.get('comment')
    db.session.commit()
    return redirect(url_for('admin.manage_returns'))


@routes.route('/sellers')
@admin_required
def manage_sellers():
    """View and manage all sellers"""
    status_filter = request.args.get('status', 'all')
    
    query = SellerProfile.query
    
    if status_filter != 'all':
        try:
            status = SellerStatus(status_filter)
            query = query.filter_by(status=status)
        except ValueError:
            pass
    
    sellers = query.order_by(SellerProfile.id.desc()).all()
    
    return render_template(
        'admin/sellers.html',
        sellers=sellers,
        current_status=status_filter
    )


@routes.route('/sellers/<int:seller_id>/approve', methods=['POST'])
@admin_required
def approve_seller(seller_id):
    """Approve a seller application"""
    seller = SellerProfile.query.get_or_404(seller_id)
    seller.status = SellerStatus.ACTIVE
    seller.is_verified = True
    
    from datetime import datetime
    seller.verified_at = datetime.utcnow()
    
    db.session.commit()
    
    flash(f'Seller "{seller.display_name}" has been approved!', 'success')
    return redirect(url_for('admin.manage_sellers'))


@routes.route('/sellers/<int:seller_id>/reject', methods=['POST'])
@admin_required
def reject_seller(seller_id):
    """Reject a seller application"""
    seller = SellerProfile.query.get_or_404(seller_id)
    
    # Delete the seller profile and associated user
    user = seller.user
    db.session.delete(seller)
    db.session.delete(user)
    db.session.commit()
    
    flash(f'Seller application rejected and removed.', 'info')
    return redirect(url_for('admin.manage_sellers'))


@routes.route('/sellers/<int:seller_id>/delete', methods=['POST'])
@admin_required
def delete_seller(seller_id):
    """Delete a seller permanently"""
    seller = SellerProfile.query.get_or_404(seller_id)
    seller_name = seller.display_name
    
    # Delete the seller profile and associated user
    user = seller.user
    db.session.delete(seller)
    db.session.delete(user)
    db.session.commit()
    
    flash(f'Seller "{seller_name}" has been permanently deleted.', 'success')
    return redirect(url_for('admin.manage_sellers'))


@routes.route('/sellers/<int:seller_id>/suspend', methods=['POST'])
@admin_required
def suspend_seller(seller_id):
    """Suspend an active seller"""
    seller = SellerProfile.query.get_or_404(seller_id)
    seller.status = SellerStatus.SUSPENDED
    
    db.session.commit()
    
    flash(f'Seller "{seller.display_name}" has been suspended.', 'warning')
    return redirect(url_for('admin.manage_sellers'))


@routes.route('/sellers/<int:seller_id>/activate', methods=['POST'])
@admin_required
def activate_seller(seller_id):
    """Reactivate a suspended seller"""
    seller = SellerProfile.query.get_or_404(seller_id)
    seller.status = SellerStatus.ACTIVE
    
    db.session.commit()
    
    flash(f'Seller "{seller.display_name}" has been reactivated.', 'success')
    return redirect(url_for('admin.manage_sellers'))


# ============================================================================
# CATEGORY MANAGEMENT ROUTES
# ============================================================================

def generate_slug(name):
    """Generate URL-friendly slug from category name"""
    slug = name.lower()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug.strip('-')


@routes.route('/categories')
@admin_required
def manage_categories():
    """View and manage all categories"""
    categories = Category.query.order_by(Category.name).all()
    
    # Get product count for each category
    category_data = []
    for category in categories:
        product_count = Product.query.filter_by(category_id=category.id).count()
        category_data.append({
            'category': category,
            'product_count': product_count
        })
    
    return render_template(
        'admin/categories.html',
        category_data=category_data
    )


@routes.route('/categories/add', methods=['GET', 'POST'])
@admin_required
def add_category():
    """Add a new category"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        
        if not name:
            flash('Category name is required.', 'danger')
            return redirect(url_for('admin.add_category'))
        
        # Generate slug
        slug = generate_slug(name)
        
        # Check if category with same name or slug exists
        existing = Category.query.filter(
            (Category.name == name) | (Category.slug == slug)
        ).first()
        
        if existing:
            flash('A category with this name already exists.', 'danger')
            return redirect(url_for('admin.add_category'))
        
        # Create new category
        category = Category(
            name=name,
            slug=slug,
            description=description if description else None
        )
        
        db.session.add(category)
        db.session.commit()
        
        flash(f'Category "{name}" has been created successfully!', 'success')
        return redirect(url_for('admin.manage_categories'))
    
    return render_template('admin/category_form.html', category=None, action='Add')


@routes.route('/categories/<int:category_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_category(category_id):
    """Edit an existing category"""
    category = Category.query.get_or_404(category_id)
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        
        if not name:
            flash('Category name is required.', 'danger')
            return redirect(url_for('admin.edit_category', category_id=category_id))
        
        # Generate new slug
        slug = generate_slug(name)
        
        # Check if another category has the same name or slug
        existing = Category.query.filter(
            Category.id != category_id,
            (Category.name == name) | (Category.slug == slug)
        ).first()
        
        if existing:
            flash('Another category with this name already exists.', 'danger')
            return redirect(url_for('admin.edit_category', category_id=category_id))
        
        # Update category
        category.name = name
        category.slug = slug
        category.description = description if description else None
        
        db.session.commit()
        
        flash(f'Category "{name}" has been updated successfully!', 'success')
        return redirect(url_for('admin.manage_categories'))
    
    return render_template('admin/category_form.html', category=category, action='Edit')


@routes.route('/categories/<int:category_id>/delete', methods=['POST'])
@admin_required
def delete_category(category_id):
    """Delete a category"""
    category = Category.query.get_or_404(category_id)
    
    # Check if category has products
    product_count = Product.query.filter_by(category_id=category_id).count()
    
    if product_count > 0:
        flash(
            f'Cannot delete category "{category.name}" because it has {product_count} product(s) associated with it. '
            f'Please reassign or delete those products first.',
            'danger'
        )
        return redirect(url_for('admin.manage_categories'))
    
    category_name = category.name
    db.session.delete(category)
    db.session.commit()
    
    flash(f'Category "{category_name}" has been deleted successfully!', 'success')
    return redirect(url_for('admin.manage_categories'))
