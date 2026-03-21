from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, User, UserType, SellerProfile, SellerStatus, Product, Category, Order, OrderItem, OrderStatus, Withdrawal
from utils.auth import login_required, seller_required, active_seller_required
from werkzeug.utils import secure_filename
import os

routes = Blueprint('seller', __name__)

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@routes.route('/become_seller', methods=['GET', 'POST'])
def become_seller():
    # If user is logged in, check if they already have a seller profile
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user and user.seller_profile:
            if user.seller_profile.status == SellerStatus.ACTIVE:
                flash('You are already an active seller.', 'info')
            else:
                flash('You have already applied for a seller account. Your application is under review.', 'info')
            return redirect(url_for('seller.dashboard'))

    if request.method == 'POST':
        if 'user_id' not in session:
            username = request.form['username']
            password = request.form['password']
            confirm_password = request.form['confirm_password']

            if password != confirm_password:
                flash('Passwords do not match.', 'error')
                return redirect(url_for('seller.become_seller'))
            elif User.query.filter_by(username=username).first():
                flash('Username already exists.', 'error')
                return redirect(url_for('seller.become_seller'))
            # create new user as seller
            new_user = User(username=username, user_type=UserType.SELLER)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            session['user_id'] = new_user.id
            session['user_type'] = new_user.user_type.value
            session['username'] = username
            # create new seller profile
            display_name = request.form['display_name']
            company_name = request.form.get('company_name')
            description = request.form.get('description')
            business_email = request.form.get('business_email')
            business_phone = request.form.get('business_phone')
            website_url = request.form.get('website_url')
            new_seller = SellerProfile(
                user_id=new_user.id,
                display_name=display_name,
                company_name=company_name,
                description=description,
                business_email=business_email,
                business_phone=business_phone,
                website_url=website_url,
                status=SellerStatus.PENDING
            )
            db.session.add(new_seller)
            db.session.commit()
            flash('Seller account account application submitted successfully!', 'success')
            return redirect(url_for('seller.dashboard'))

        # This part shouldn't be reached if they are already a seller,
        # but kept as a secondary safety check.
        user = User.query.get(session['user_id'])
        if not user:
            flash('User not found.', 'error')
            return redirect(url_for('auth.login'))

        display_name = request.form['display_name']
        company_name = request.form.get('company_name')
        description = request.form.get('description')
        business_email = request.form.get('business_email')
        business_phone = request.form.get('business_phone')
        website_url = request.form.get('website_url')

        new_seller = SellerProfile(
            user_id=user.id,
            display_name=display_name,
            company_name=company_name,
            description=description,
            business_email=business_email,
            business_phone=business_phone,
            website_url=website_url,
            status=SellerStatus.PENDING
        )

        db.session.add(new_seller)
        db.session.commit()

        flash('You have successfully applied to become a seller!', 'success')
        return redirect(url_for('seller.dashboard'))

    return render_template('sellerregister.html')


@routes.route('/dashboard')
@seller_required
def dashboard():
    """Seller dashboard with analytics"""
    user_id = session['user_id']
    
    # Get seller's products
    products = Product.query.filter_by(seller_id=user_id).all()
    
    # Get seller's orders
    product_ids = [p.id for p in products]
    from models import ProductVariant
    orders = Order.query.join(OrderItem).join(ProductVariant).filter(
        ProductVariant.product_id.in_(product_ids)
    ).distinct().order_by(Order.created_at.desc()).limit(10).all()
    
    # Calculate analytics
    total_products = len(products)
    
    # Total revenue from seller's products in paid/delivered orders
    from sqlalchemy import func
    total_revenue = db.session.query(func.sum(OrderItem.quantity * OrderItem.price_at_purchase)).join(ProductVariant).filter(
        ProductVariant.product_id.in_(product_ids)
    ).join(Order).filter(
        Order.status.in_([OrderStatus.PAID, OrderStatus.PROCESSING, OrderStatus.SHIPPED, OrderStatus.DELIVERED])
    ).scalar() or 0
    
    # Correct in_stock/out_of_stock by checking if ANY variant has stock
    # We join with variants and check for any positive stock
    in_stock_ids = db.session.query(ProductVariant.product_id).filter(
        ProductVariant.product_id.in_(product_ids),
        ProductVariant.stock > 0
    ).distinct().all()
    in_stock_ids = [r[0] for r in in_stock_ids]
    
    in_stock_count = len(in_stock_ids)
    out_of_stock_count = total_products - in_stock_count

    
    seller_profile = User.query.get(user_id).seller_profile
    
    return render_template(
        'seller/dashboard.html',
        products=products[:5],  # Show only 5 recent products
        orders=orders,
        total_products=total_products,
        total_sales=total_revenue,
        balance=seller_profile.balance,
        in_stock=in_stock_count,
        out_of_stock=out_of_stock_count
    )


@routes.route('/products')
@seller_required
def products():
    """List all seller's products"""
    user_id = session['user_id']
    products = Product.query.filter_by(seller_id=user_id).order_by(Product.created_at.desc()).all()
    
    return render_template('seller/products.html', products=products)


@routes.route('/products/add', methods=['GET', 'POST'])
@active_seller_required
def add_product():
    """Add new product"""
    if request.method == 'POST':
        user_id = session['user_id']
        
        name = request.form.get('name')
        description = request.form.get('description')
        price = float(request.form.get('price'))
        quantity = int(request.form.get('quantity'))
        category_id = request.form.get('category_id')
        
        if not category_id:
            category_id = None
        
        # Handle image upload
        images_list = []
        if 'images' in request.files:
            files = request.files.getlist('images')
            for file in files:
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    # Add timestamp to avoid conflicts
                    from datetime import datetime
                    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                    filename = f"{timestamp}_{filename}"
                    
                    # Create upload folder if it doesn't exist
                    upload_path = os.path.join(UPLOAD_FOLDER)
                    os.makedirs(upload_path, exist_ok=True)
                    
                    file.save(os.path.join(upload_path, filename))
                    images_list.append(filename)
        
        images_str = ','.join(images_list) if images_list else None
        
        product = Product(
            name=name,
            description=description,
            price=price,
            quantity=quantity, # Keep for backward compatibility or overview
            category_id=category_id,
            seller_id=user_id,
            images=images_str
        )
        db.session.add(product)
        db.session.flush()

        # Create default variant
        from models import ProductVariant
        variant = ProductVariant(
            product_id=product.id,
            name="Default",
            price=price,
            stock=quantity,
            sku=f"SKU-{product.id}-DEF"
        )
        db.session.add(variant)
        db.session.commit()
        
        flash('Product added successfully!', 'success')
        return redirect(url_for('seller.products'))
    
    categories = Category.query.all()
    return render_template('seller/product_form.html', categories=categories, product=None)


@routes.route('/products/<int:product_id>/edit', methods=['GET', 'POST'])
@active_seller_required
def edit_product(product_id):
    """Edit existing product"""
    user_id = session['user_id']
    product = Product.query.filter_by(id=product_id, seller_id=user_id).first_or_404()
    
    if request.method == 'POST':
        product.name = request.form.get('name')
        product.description = request.form.get('description')
        product.price = float(request.form.get('price'))
        product.quantity = int(request.form.get('quantity'))
        category_id = request.form.get('category_id')
        product.category_id = category_id if category_id else None
        
        # Handle image upload
        if 'images' in request.files:
            files = request.files.getlist('images')
            images_list = product.get_image_list()  # Keep existing images
            
            for file in files:
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    from datetime import datetime
                    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                    filename = f"{timestamp}_{filename}"
                    
                    upload_path = os.path.join(UPLOAD_FOLDER)
                    os.makedirs(upload_path, exist_ok=True)
                    
                    file.save(os.path.join(upload_path, filename))
                    images_list.append(filename)
            
            product.images = ','.join(images_list) if images_list else None
        
        db.session.commit()
        
        flash('Product updated successfully!', 'success')
        return redirect(url_for('seller.products'))
    
    categories = Category.query.all()
    return render_template('seller/product_form.html', categories=categories, product=product)


@routes.route('/products/<int:product_id>/delete', methods=['POST'])
@active_seller_required
def delete_product(product_id):
    """Delete product"""
    user_id = session['user_id']
    product = Product.query.filter_by(id=product_id, seller_id=user_id).first_or_404()
    
    # Delete associated images
    for image in product.get_image_list():
        try:
            os.remove(os.path.join(UPLOAD_FOLDER, image))
        except:
            pass
    
    db.session.delete(product)
    db.session.commit()
    
    flash('Product deleted successfully!', 'info')
    return redirect(url_for('seller.products'))


@routes.route('/orders')
@seller_required
def orders():
    """View seller's product order items grouped by product"""
    user_id = session['user_id']
    
    # Get active order items (pending, processing, shipped) - newest first
    from models import ProductVariant
    active_items = db.session.query(OrderItem).join(ProductVariant).join(Product).join(Order).filter(
        Product.seller_id == user_id,
        Order.status.in_([OrderStatus.PENDING, OrderStatus.PROCESSING, OrderStatus.SHIPPED])
    ).order_by(Order.created_at.asc()).all()
    
    # Get completed/cancelled order items - newest first
    completed_items = db.session.query(OrderItem).join(ProductVariant).join(Product).join(Order).filter(
        Product.seller_id == user_id,
        Order.status.in_([OrderStatus.DELIVERED, OrderStatus.CANCELLED])
    ).order_by(Order.created_at.desc()).all()
    
    # Combine: active first, then completed
    order_items = active_items + completed_items
    
    # Group order items by product
    from collections import defaultdict
    products_orders = defaultdict(list)
    for item in order_items:
        # Use variant's product_id
        pid = item.variant.product_id
        products_orders[pid].append(item)
    
    return render_template('seller/orders.html', 
                         products_orders=products_orders, 
                         order_items=order_items,
                         active_count=len(active_items),
                         completed_count=len(completed_items))

@routes.route('/orders/<int:order_id>/update-status', methods=['POST'])
@seller_required
def update_order_status(order_id):
    """Update order status"""
    user_id = session['user_id']
    
    # Get the order
    order = Order.query.get_or_404(order_id)
    
    # Prevent updating status for delivered or cancelled orders
    if order.status in [OrderStatus.DELIVERED, OrderStatus.CANCELLED]:
        flash(f'Cannot update status for {order.status.value} orders.', 'error')
        return redirect(url_for('seller.orders'))
    
    # Verify this seller has products in this order
    product_ids = [p.id for p in Product.query.filter_by(seller_id=user_id).all()]
    from models import ProductVariant
    has_products = db.session.query(OrderItem).join(ProductVariant).filter(
        OrderItem.order_id == order_id,
        ProductVariant.product_id.in_(product_ids)
    ).first()
    
    if not has_products:
        flash('You do not have permission to update this order.', 'error')
        return redirect(url_for('seller.orders'))
    
    # Get new status from form
    new_status = request.form.get('status')
    
    try:
        # Update order status
        old_status = order.status
        order.status = OrderStatus(new_status)
        
        # Credit seller balance if order is delivered
        if new_status == OrderStatus.DELIVERED.value and old_status != OrderStatus.DELIVERED:
            # We need to credit all sellers who had items in this order
            # The current seller might only be one of them
            for item in order.items:
                # Use the property helper to get the product
                product = item.product
                if product:
                    # Get the seller of this specific product
                    item_seller = User.query.get(product.seller_id)
                    if item_seller and item_seller.seller_profile:
                        item_seller.seller_profile.balance += (item.price_at_purchase * item.quantity)
        
        db.session.commit()
        flash(f'Order #{order.id} status updated to {new_status.title()}!', 'success')
    except ValueError:
        flash('Invalid status value.', 'error')
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating status: {str(e)}', 'error')
    
    return redirect(url_for('seller.orders'))

@routes.route('/reports')
@seller_required
def reports():
    """Seller analytics and reports dashboard"""
    from datetime import datetime, timedelta
    from sqlalchemy import func

    user_id = session['user_id']

    # Seller products
    products = Product.query.filter_by(seller_id=user_id).all()
    product_ids = [p.id for p in products]

    # Defaults
    total_revenue = 0
    total_products_sold = 0
    total_orders = 0
    top_products = []
    sales_dates = []
    sales_revenue = []
    sales_quantity = []
    status_counts = {
        'pending': 0,
        'processing': 0,
        'shipped': 0,
        'delivered': 0,
        'cancelled': 0
    }

    if product_ids:
        # ---------- ORDER STATUS (COUNT UNIQUE ORDERS) ----------
        from models import ProductVariant
        orders = (
            db.session.query(Order.id, Order.status)
            .join(OrderItem, OrderItem.order_id == Order.id)
            .join(ProductVariant, ProductVariant.id == OrderItem.variant_id)
            .filter(ProductVariant.product_id.in_(product_ids))
            .distinct()
            .all()
        )

        total_orders = len(orders)

        for _, status in orders:
            status_counts[status.value] += 1

        # ---------- DELIVERED SALES ONLY ----------
        from models import ProductVariant
        delivered_items = (
            db.session.query(OrderItem)
            .join(Order, Order.id == OrderItem.order_id)
            .join(ProductVariant, ProductVariant.id == OrderItem.variant_id)
            .filter(
                ProductVariant.product_id.in_(product_ids),
                Order.status == OrderStatus.DELIVERED
            )
            .all()
        )

        total_revenue = sum(
            item.price_at_purchase * item.quantity for item in delivered_items
        )
        total_products_sold = sum(item.quantity for item in delivered_items)

        # ---------- TOP PRODUCTS ----------
        product_sales = {}
        product_revenue = {}

        for item in delivered_items:
            pid = item.variant.product_id
            product_sales[pid] = product_sales.get(pid, 0) + item.quantity
            product_revenue[pid] = product_revenue.get(
                pid, 0
            ) + item.price_at_purchase * item.quantity

        top_ids = sorted(
            product_sales,
            key=lambda x: product_sales[x],
            reverse=True
        )[:5]

        products_map = {
            p.id: p for p in Product.query.filter(Product.id.in_(top_ids)).all()
        }

        top_products = [
            {
                'name': products_map[pid].name,
                'quantity': product_sales[pid],
                'revenue': product_revenue[pid]
            }
            for pid in top_ids if pid in products_map
        ]

        # ---------- SALES OVER TIME (LAST 30 DAYS) ----------
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)

        from models import ProductVariant
        daily_sales = (
            db.session.query(
                func.date(Order.created_at).label('date'),
                func.sum(OrderItem.quantity * OrderItem.price_at_purchase).label('revenue'),
                func.sum(OrderItem.quantity).label('quantity')
            )
            .join(OrderItem, OrderItem.order_id == Order.id)
            .join(ProductVariant, ProductVariant.id == OrderItem.variant_id)
            .filter(
                ProductVariant.product_id.in_(product_ids),
                Order.status == OrderStatus.DELIVERED,
                Order.created_at >= thirty_days_ago
            )
            .group_by(func.date(Order.created_at))
            .order_by('date')
            .all()
        )

        sales_dates = [
            d.date.strftime('%Y-%m-%d') if not isinstance(d.date, str) else d.date
            for d in daily_sales
        ]
        sales_revenue = [float(d.revenue or 0) for d in daily_sales]
        sales_quantity = [int(d.quantity or 0) for d in daily_sales]

    return render_template(
        'seller/reports.html',
        total_revenue=total_revenue,
        total_products_sold=total_products_sold,
        total_orders=total_orders,
        top_products=top_products,
        sales_dates=sales_dates,
        sales_revenue=sales_revenue,
        sales_quantity=sales_quantity,
        status_counts=status_counts,
        total_products=len(products)
    )

@routes.route('/withdrawals', methods=['GET'])
@seller_required
def withdrawals():
    """List seller withdrawal requests and handle new requests"""
    user_id = session['user_id']
    seller = User.query.get(user_id)
    
    withdrawals_list = Withdrawal.query.filter_by(seller_id=user_id).order_by(Withdrawal.created_at.desc()).all()
    
    return render_template(
        'seller/withdrawals.html',
        withdrawals=withdrawals_list,
        balance=seller.seller_profile.balance,
        seller=seller.seller_profile
    )

@routes.route('/withdrawals/request', methods=['POST'])
@seller_required
def request_withdrawal():
    """Submit a new withdrawal request"""
    user_id = session['user_id']
    seller = User.query.get(user_id)
    
    amount = float(request.form.get('amount', 0))
    bank_name = request.form.get('bank_name')
    account_number = request.form.get('account_number')
    other_details = request.form.get('other_details')
    
    if amount <= 0:
        flash('Amount must be greater than zero.', 'error')
        return redirect(url_for('seller.withdrawals'))
        
    if amount > seller.seller_profile.balance:
        flash('Insufficient balance.', 'error')
        return redirect(url_for('seller.withdrawals'))
        
    # Create withdrawal request
    withdrawal = Withdrawal(
        seller_id=user_id,
        amount=amount,
        bank_name=bank_name,
        bank_account_number=account_number,
        other_method_details=other_details,
        status='pending'
    )
    
    # Save these details to the seller's profile for next time
    seller.seller_profile.last_bank_name = bank_name
    seller.seller_profile.last_account_number = account_number
    
    # Deduct from balance immediately to lock the funds
    seller.seller_profile.balance -= amount
    
    db.session.add(withdrawal)
    db.session.commit()
    
    flash(f'Withdrawal request for ₹{amount:.2f} submitted successfully!', 'success')
    return redirect(url_for('seller.withdrawals'))
