from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, Order, OrderItem, Product, SellerProfile, OrderStatus
from utils.auth import login_required, seller_required
from werkzeug.utils import secure_filename
import os

routes = Blueprint('seller', __name__)


@routes.route('/orders')
@login_required
@seller_required
def orders():
    """View orders containing seller's products"""
    user_id = session['user_id']
    
    # Get all orders that contain this seller's products
    orders_list = db.session.query(Order).join(OrderItem).join(Product).filter(
        Product.seller_id == user_id
    ).distinct().order_by(Order.created_at.desc()).all()
    
    return render_template('seller/orders.html', orders=orders_list)


@routes.route('/orders/<int:order_id>/update_status', methods=['POST'])
@login_required
@seller_required
def update_order_status(order_id):
    """Update order status"""
    user_id = session['user_id']
    
    # Get the order
    order = Order.query.get_or_404(order_id)
    
    # Verify this seller has products in this order
    has_products = db.session.query(OrderItem).join(Product).filter(
        OrderItem.order_id == order_id,
        Product.seller_id == user_id
    ).first()
    
    if not has_products:
        flash('You do not have permission to update this order.', 'error')
        return redirect(url_for('seller.orders'))
    
    # Get new status from form
    new_status = request.form.get('status')
    
    try:
        # Update order status
        order.status = OrderStatus(new_status)
        db.session.commit()
        flash(f'Order status updated to {new_status}!', 'success')
    except ValueError:
        flash('Invalid status value.', 'error')
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating status: {str(e)}', 'error')
    
    return redirect(url_for('seller.orders'))
