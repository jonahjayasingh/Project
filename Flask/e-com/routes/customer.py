from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, current_app
from models import db, User, Product, Cart, Order, OrderItem, OrderStatus, Profile
from utils.auth import login_required

routes = Blueprint('customer', __name__)


@routes.route('/cart')
@login_required
def view_cart():
    """Display shopping cart"""
    user_id = session['user_id']
    cart_items = Cart.query.filter_by(user_id=user_id).all()
    
    total = sum(item.get_subtotal() for item in cart_items)
    
    return render_template('customer/cart.html', cart_items=cart_items, total=total)


@routes.route('/cart/add/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    """Add product to cart"""
    user_id = session['user_id']
    quantity = int(request.form.get('quantity', 1))
    
    # Check if product exists and has stock
    product = Product.query.get_or_404(product_id)
    
    # Prevent adding out-of-stock products
    if product.quantity == 0:
        flash('This product is out of stock and cannot be added to cart.', 'error')
        return redirect(url_for('product.product_detail', product_id=product_id))
    
    if product.quantity < quantity:
        flash('Not enough stock available.', 'error')
        return redirect(url_for('product.product_detail', product_id=product_id))
    
    # Check if item already in cart
    cart_item = Cart.query.filter_by(user_id=user_id, product_id=product_id).first()
    
    if cart_item:
        # Update quantity
        new_quantity = cart_item.quantity + quantity
        if product.quantity < new_quantity:
            flash('Not enough stock available.', 'error')
            return redirect(url_for('product.product_detail', product_id=product_id))
        cart_item.quantity = new_quantity
    else:
        # Create new cart item
        cart_item = Cart(user_id=user_id, product_id=product_id, quantity=quantity)
        db.session.add(cart_item)
    
    db.session.commit()
    flash('Product added to cart!', 'success')
    return redirect(url_for('customer.view_cart'))


@routes.route('/cart/update/<int:product_id>', methods=['POST'])
@login_required
def update_cart(product_id):
    """Update cart item quantity"""
    user_id = session['user_id']
    quantity = int(request.form.get('quantity', 1))
    
    cart_item = Cart.query.filter_by(user_id=user_id, product_id=product_id).first_or_404()
    product = Product.query.get(product_id)
    
    if quantity <= 0:
        db.session.delete(cart_item)
        flash('Item removed from cart.', 'info')
    elif product.quantity < quantity:
        flash('Not enough stock available.', 'error')
        return redirect(url_for('customer.view_cart'))
    else:
        cart_item.quantity = quantity
        flash('Cart updated.', 'success')
    
    db.session.commit()
    return redirect(url_for('customer.view_cart'))


@routes.route('/cart/remove/<int:product_id>', methods=['POST'])
@login_required
def remove_from_cart(product_id):
    """Remove item from cart"""
    user_id = session['user_id']
    cart_item = Cart.query.filter_by(user_id=user_id, product_id=product_id).first_or_404()
    
    db.session.delete(cart_item)
    db.session.commit()
    
    flash('Item removed from cart.', 'info')
    return redirect(url_for('customer.view_cart'))


@routes.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    """Checkout process"""
    user_id = session['user_id']
    cart_items = Cart.query.filter_by(user_id=user_id).all()
    
    if not cart_items:
        flash('Your cart is empty.', 'error')
        return redirect(url_for('customer.view_cart'))
    
    # Check if customer has completed profile
    profile = Profile.query.filter_by(user_id=user_id).first()
    if not profile or not profile.full_name or not profile.phone_number or not profile.address:
        flash('Please complete your profile before placing an order.', 'warning')
        return redirect(url_for('customer.profile'))

    if request.method == 'POST':
        # Get shipping address
        shipping_address = request.form.get('shipping_address')
        
        if not shipping_address or not shipping_address.strip():
            flash('Please provide a shipping address.', 'error')
            return redirect(url_for('customer.checkout'))
        
        # Calculate total
        total = sum(item.get_subtotal() for item in cart_items)
        
        try:
            # Create order
            order = Order(
                user_id=user_id,
                total_amount=total,
                shipping_address=shipping_address,
                status=OrderStatus.PENDING
            )
            db.session.add(order)
            db.session.flush()  # Get order ID
        
            # Create order items and update product quantities
            for cart_item in cart_items:
                product = cart_item.product
                
                # Check stock again
                if product.quantity < cart_item.quantity:
                    db.session.rollback()
                    flash(f'Not enough stock for {product.name}.', 'error')
                    return redirect(url_for('customer.view_cart'))
                
                # Create order item
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=product.id,
                    quantity=cart_item.quantity,
                    price_at_purchase=product.price,
                    product_name=product.name
                )
                db.session.add(order_item)
                
                # Update product quantity
                product.quantity -= cart_item.quantity
            
            # Clear cart
            for cart_item in cart_items:
                db.session.delete(cart_item)
            
            db.session.commit()
            flash('Order placed successfully!', 'success')
            return redirect(url_for('customer.order_detail', order_id=order.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'error')
            return redirect(url_for('customer.checkout'))
    
    total = sum(item.get_subtotal() for item in cart_items)
    
    # Get user profile for default address
    profile = Profile.query.filter_by(user_id=user_id).first()
    
    return render_template(
        'customer/checkout.html',
        cart_items=cart_items,
        total=total,
        profile=profile
    )


@routes.route('/orders')
@login_required
def orders():
    """View order history"""
    user_id = session['user_id']
    
    # Get active orders (pending, processing, shipped) - newest first
    active_orders = Order.query.filter_by(user_id=user_id).filter(
        Order.status.in_([OrderStatus.PENDING, OrderStatus.PROCESSING, OrderStatus.SHIPPED])
    ).order_by(Order.created_at.desc()).all()
    
    # Get completed/cancelled orders - newest first
    completed_orders = Order.query.filter_by(user_id=user_id).filter(
        Order.status.in_([OrderStatus.DELIVERED, OrderStatus.CANCELLED])
    ).order_by(Order.created_at.desc()).all()
    
    # Combine: active orders first, then completed
    orders = active_orders + completed_orders
    
    return render_template('customer/orders.html', orders=orders, 
                         active_count=len(active_orders), 
                         completed_count=len(completed_orders))


@routes.route('/orders/<int:order_id>')
@login_required
def order_detail(order_id):
    """View order details"""
    user_id = session['user_id']
    order = Order.query.filter_by(id=order_id, user_id=user_id).first_or_404()
    
    return render_template('customer/order_detail.html', order=order)


@routes.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """Customer profile management"""
    user_id = session['user_id']
    user_profile = Profile.query.filter_by(user_id=user_id).first()
    
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        address = request.form.get('address')
        phone_number = request.form.get('phone_number')
        
        if user_profile:
            user_profile.full_name = full_name
            user_profile.address = address
            user_profile.phone_number = phone_number
        else:
            user_profile = Profile(
                user_id=user_id,
                full_name=full_name,
                address=address,
                phone_number=phone_number
            )
            db.session.add(user_profile)
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('customer.profile'))
    
    return render_template('customer/profile.html', profile=user_profile)


@routes.route('/products/<int:product_id>/review', methods=['POST'])
@login_required
def submit_review(product_id):
    """Submit a product review"""
    from models import Review, OrderItem
    
    user_id = session['user_id']
    product = Product.query.get_or_404(product_id)
    
    # Check if user has purchased this product
    has_purchased = db.session.query(OrderItem).join(Order).filter(
        Order.user_id == user_id,
        OrderItem.product_id == product_id
    ).first()
    
    if not has_purchased:
        flash('You can only review products you have purchased.', 'error')
        return redirect(url_for('product.product_detail', product_id=product_id))
    
    # Check if user already reviewed this product
    existing_review = Review.query.filter_by(
        user_id=user_id,
        product_id=product_id
    ).first()
    
    if existing_review:
        flash('You have already reviewed this product.', 'error')
        return redirect(url_for('product.product_detail', product_id=product_id))
    
    # Get form data
    rating = request.form.get('rating', type=int)
    comment = request.form.get('comment', '').strip()
    
    # Validate rating
    if not rating or rating < 1 or rating > 5:
        flash('Please provide a rating between 1 and 5 stars.', 'error')
        return redirect(url_for('product.product_detail', product_id=product_id))
    
    try:
        review = Review(
            user_id=user_id,
            product_id=product_id,
            rating=rating,
            comment=comment if comment else None
        )
        
        db.session.add(review)
        db.session.commit()
        
        flash('Thank you for your review!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error submitting review: {str(e)}', 'error')
    
    return redirect(url_for('product.product_detail', product_id=product_id))
