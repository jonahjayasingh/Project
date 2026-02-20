from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import User, SellerProfile, SellerStatus, Category, Product, db
from utils.auth import admin_required
import re

routes = Blueprint('admin', __name__)


@routes.route('/dashboard')
@admin_required
def dashboard():
    """Admin dashboard with overview"""
    # Get statistics
    total_users = User.query.count()
    total_sellers = SellerProfile.query.count()
    pending_sellers = SellerProfile.query.filter_by(status=SellerStatus.PENDING).count()
    active_sellers = SellerProfile.query.filter_by(status=SellerStatus.ACTIVE).count()
    
    return render_template(
        'admin/dashboard.html',
        total_users=total_users,
        total_sellers=total_sellers,
        pending_sellers=pending_sellers,
        active_sellers=active_sellers
    )


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
