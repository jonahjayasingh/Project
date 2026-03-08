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
    
    # Check for coupon in session
    coupon_code = session.get('coupon_code')
    coupon = None
    discount = 0
    if coupon_code:
        from models import Coupon
        coupon = Coupon.query.filter_by(code=coupon_code).first()
        if coupon and coupon.is_valid(total):
            discount = coupon.calculate_discount(total)
        else:
            session.pop('coupon_code', None)
    
    return render_template('customer/cart.html', cart_items=cart_items, total=total, discount=discount, coupon=coupon)


@routes.route('/cart/add', methods=['POST'])
@login_required
def add_item_to_cart():
    """Add variant to cart"""
    user_id = session['user_id']
    variant_id = request.form.get('variant_id', type=int)
    quantity = int(request.form.get('quantity', 1))
    
    if not variant_id:
        flash('Invalid product variant selected.', 'error')
        return redirect(request.referrer or url_for('product.list_products'))
    
    # Check if variant exists and has stock
    from models import ProductVariant
    variant = ProductVariant.query.get_or_404(variant_id)
    
    if variant.stock < quantity:
        flash('Not enough stock available.', 'error')
        return redirect(url_for('product.product_detail', product_id=variant.product_id))
    
    # Check if item already in cart
    cart_item = Cart.query.filter_by(user_id=user_id, variant_id=variant_id).first()
    
    if cart_item:
        if variant.stock < cart_item.quantity + quantity:
            flash('Not enough stock available.', 'error')
            return redirect(url_for('product.product_detail', product_id=variant.product_id))
        cart_item.quantity += quantity
    else:
        cart_item = Cart(user_id=user_id, variant_id=variant_id, quantity=quantity)
        db.session.add(cart_item)
    
    db.session.commit()
    flash('Added to cart!', 'success')
    return redirect(url_for('customer.view_cart'))


@routes.route('/cart/update/<int:variant_id>', methods=['POST'])
@login_required
def update_cart(variant_id):
    """Update cart item quantity"""
    user_id = session['user_id']
    quantity = int(request.form.get('quantity', 1))
    
    from models import ProductVariant
    cart_item = Cart.query.filter_by(user_id=user_id, variant_id=variant_id).first_or_404()
    variant = ProductVariant.query.get(variant_id)
    
    if quantity <= 0:
        db.session.delete(cart_item)
        flash('Item removed from cart.', 'info')
    elif variant and variant.stock < quantity:
        flash('Not enough stock available.', 'error')
        return redirect(url_for('customer.view_cart'))
    else:
        cart_item.quantity = quantity
        flash('Cart updated.', 'success')
    
    db.session.commit()
    return redirect(url_for('customer.view_cart'))


@routes.route('/cart/remove/<int:variant_id>', methods=['POST'])
@login_required
def remove_from_cart(variant_id):
    """Remove item from cart"""
    user_id = session['user_id']
    cart_item = Cart.query.filter_by(user_id=user_id, variant_id=variant_id).first_or_404()
    
    db.session.delete(cart_item)
    db.session.commit()
    
    flash('Item removed from cart.', 'info')
    return redirect(url_for('customer.view_cart'))


@routes.route('/wishlist/add/<int:product_id>', methods=['POST'])
@login_required
def add_to_wishlist(product_id):
    """Add product to wishlist"""
    from models import Wishlist
    user_id = session['user_id']
    
    # Check if already in wishlist
    existing = Wishlist.query.filter_by(user_id=user_id, product_id=product_id).first()
    if existing:
        flash('Product is already in your wishlist.', 'info')
    else:
        wish = Wishlist(user_id=user_id, product_id=product_id)
        db.session.add(wish)
        db.session.commit()
        flash('Added to wishlist!', 'success')
        
    return redirect(url_for('product.product_detail', product_id=product_id))


@routes.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    """Checkout process with Addresses and Coupons"""
    user_id = session['user_id']
    from models import Address, Coupon
    cart_items = Cart.query.filter_by(user_id=user_id).all()
    
    if not cart_items:
        flash('Cart is empty.', 'error')
        return redirect(url_for('customer.view_cart'))
    
    addresses = Address.query.filter_by(user_id=user_id).all()
    if not addresses:
        flash('Please add a shipping address first.', 'warning')
        return redirect(url_for('customer.add_address'))

    total = sum(item.get_subtotal() for item in cart_items)
    
    # Process coupon
    coupon_code = session.get('coupon_code')
    coupon = None
    discount = 0
    if coupon_code:
        coupon = Coupon.query.filter_by(code=coupon_code).first()
        if coupon and coupon.is_valid(total):
            discount = coupon.calculate_discount(total)
        else:
            session.pop('coupon_code', None)

    final_total = total - discount

    if request.method == 'POST':
        address_id = request.form.get('address_id')
        selected_address = Address.query.get(address_id)
        
        if not selected_address or selected_address.user_id != user_id:
            flash('Invalid address.', 'error')
            return redirect(url_for('customer.checkout'))
        
        try:
            # Create order
            order = Order(
                user_id=user_id,
                address_id=selected_address.id,
                coupon_id=coupon.id if coupon else None,
                total_amount=total,
                discount_amount=discount,
                final_amount=final_total,
                shipping_address_text=f"{selected_address.name}, {selected_address.address_line1}, {selected_address.city}, {selected_address.state} {selected_address.postal_code}, {selected_address.country}",
                status=OrderStatus.PENDING
            )
            db.session.add(order)
            db.session.flush()
        
            for cart_item in cart_items:
                variant = cart_item.variant
                
                if variant.stock < cart_item.quantity:
                    db.session.rollback()
                    flash(f'Not enough stock for {variant.product.name} ({variant.name}).', 'error')
                    return redirect(url_for('customer.view_cart'))
                
                order_item = OrderItem(
                    order_id=order.id,
                    variant_id=variant.id,
                    quantity=cart_item.quantity,
                    price_at_purchase=variant.price,
                    product_name=variant.product.name,
                    variant_name=variant.name
                )
                db.session.add(order_item)
                
                variant.stock -= cart_item.quantity
            
            db.session.commit()
            session.pop('coupon_code', None) # Clear coupon after order creation
            
            # Redirect to payment selection/stripe
            return render_template('customer/order_confirm_pay.html', order=order)
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'error')
            return redirect(url_for('customer.checkout'))
    
    return render_template(
        'customer/checkout.html',
        cart_items=cart_items,
        total=total,
        discount=discount,
        final_total=final_total,
        addresses=addresses,
        coupon=coupon
    )


@routes.route('/coupon/apply', methods=['POST'])
@login_required
def apply_coupon():
    from models import Coupon
    code = request.form.get('coupon_code')
    user_id = session['user_id']
    cart_items = Cart.query.filter_by(user_id=user_id).all()
    total = sum(item.get_subtotal() for item in cart_items)
    
    coupon = Coupon.query.filter_by(code=code).first()
    if coupon and coupon.is_valid(total):
        session['coupon_code'] = code
        flash('Coupon applied!', 'success')
    else:
        flash('Invalid or expired coupon.', 'error')
    
    return redirect(url_for('customer.view_cart'))


@routes.route('/orders/<int:order_id>/return', methods=['POST'])
@login_required
def request_return(order_id):
    from models import ReturnRequest
    user_id = session['user_id']
    order = Order.query.filter_by(id=order_id, user_id=user_id).first_or_404()
    
    if order.status != OrderStatus.DELIVERED:
        flash('Only delivered items can be returned.', 'error')
        return redirect(url_for('customer.order_detail', order_id=order_id))
    
    product_id = request.form.get('product_id')
    reason = request.form.get('reason')
    
    existing = ReturnRequest.query.filter_by(order_id=order_id, product_id=product_id).first()
    if existing:
        flash('Return request already exists for this item.', 'warning')
    else:
        ret = ReturnRequest(order_id=order_id, product_id=product_id, reason=reason)
        db.session.add(ret)
        db.session.commit()
        flash('Return request submitted.', 'success')
        
    return redirect(url_for('customer.order_detail', order_id=order_id))


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


@routes.route('/addresses')
@login_required
def addresses():
    """View saved addresses"""
    from models import Address
    user_id = session['user_id']
    addresses = Address.query.filter_by(user_id=user_id).order_by(Address.is_default.desc(), Address.created_at.desc()).all()
    return render_template('customer/addresses.html', addresses=addresses)


@routes.route('/addresses/add', methods=['GET', 'POST'])
@login_required
def add_address():
    """Add new shipping address"""
    from models import Address
    if request.method == 'POST':
        user_id = session['user_id']
        name = request.form.get('name')
        phone = request.form.get('phone')
        address_line1 = request.form.get('address_line1')
        address_line2 = request.form.get('address_line2')
        city = request.form.get('city')
        state = request.form.get('state')
        postal_code = request.form.get('postal_code')
        country = request.form.get('country', 'USA')
        is_default = 'is_default' in request.form
        
        # If this is the first address or set as default, handle it
        if is_default:
            Address.query.filter_by(user_id=user_id).update({Address.is_default: False})
        
        new_addr = Address(
            user_id=user_id,
            name=name,
            phone=phone,
            address_line1=address_line1,
            address_line2=address_line2,
            city=city,
            state=state,
            postal_code=postal_code,
            country=country,
            is_default=is_default or not Address.query.filter_by(user_id=user_id).first()
        )
        db.session.add(new_addr)
        db.session.commit()
        
        flash('Address added!', 'success')
        next_url = request.args.get('next')
        return redirect(url_for(next_url) if next_url else url_for('customer.addresses'))
        
    return render_template('customer/add_address.html')


@routes.route('/addresses/edit/<int:address_id>', methods=['GET', 'POST'])
@login_required
def edit_address(address_id):
    """Edit existing address"""
    from models import Address
    user_id = session['user_id']
    address = Address.query.filter_by(id=address_id, user_id=user_id).first_or_404()
    
    if request.method == 'POST':
        address.name = request.form.get('name')
        address.phone = request.form.get('phone')
        address.address_line1 = request.form.get('address_line1')
        address.address_line2 = request.form.get('address_line2')
        address.city = request.form.get('city')
        address.state = request.form.get('state')
        address.postal_code = request.form.get('postal_code')
        address.country = request.form.get('country', 'USA')
        
        is_default = 'is_default' in request.form
        if is_default and not address.is_default:
            Address.query.filter_by(user_id=user_id).update({Address.is_default: False})
            address.is_default = True
        
        db.session.commit()
        flash('Address updated!', 'success')
        return redirect(url_for('customer.addresses'))
        
    return render_template('customer/edit_address.html', address=address)


@routes.route('/addresses/delete/<int:address_id>', methods=['POST'])
@login_required
def delete_address(address_id):
    """Delete address"""
    from models import Address
    user_id = session['user_id']
    address = Address.query.filter_by(id=address_id, user_id=user_id).first_or_404()
    
    db.session.delete(address)
    db.session.commit()
    
    flash('Address deleted.', 'info')
    return redirect(url_for('customer.addresses'))


@routes.route('/products/<int:product_id>/review', methods=['POST'])
@login_required
def submit_review(product_id):
    """Submit a product review"""
    from models import Review, OrderItem
    
    user_id = session['user_id']
    product = Product.query.get_or_404(product_id)
    
    # Check if user has purchased this product
    from models import ProductVariant
    has_purchased = db.session.query(OrderItem).join(Order).join(ProductVariant).filter(
        Order.user_id == user_id,
        ProductVariant.product_id == product_id
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
