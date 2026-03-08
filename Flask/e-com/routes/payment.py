import os
import stripe
from flask import Blueprint, request, jsonify, redirect, url_for, current_app, render_template, session
from models import db, Order, OrderStatus, Payment, Cart, ProductVariant
from utils.auth import login_required, login_required_role

routes = Blueprint('payment', __name__)

stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

@routes.route('/create-checkout-session', methods=['POST'])
@login_required
def create_checkout_session():
    # Get the order (assume it was just created in pending state)
    order_id = request.form.get('order_id')
    order = Order.query.get_or_404(order_id)

    if order.user_id != session['user_id']:
        return jsonify({"error": "Unauthorized"}), 403

    line_items = []
    for item in order.items:
        line_items.append({
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': f"{item.product_name} - {item.variant_name}",
                },
                'unit_amount': int(item.price_at_purchase * 100),
            },
            'quantity': item.quantity,
        })

    # Add discount as a negative line item if coupon applied
    if order.discount_amount > 0:
        line_items.append({
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': f"Discount ({order.coupon.code if order.coupon else 'Coupon'})",
                },
                'unit_amount': -int(order.discount_amount * 100),
            },
            'quantity': 1,
        })

    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url=url_for('payment.payment_success', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=url_for('payment.payment_cancel', _external=True),
            metadata={
                'order_id': order.id,
                'user_id': session['user_id']
            }
        )

        # Store session ID
        payment = Payment(
            order_id=order.id,
            stripe_session_id=checkout_session.id,
            amount=order.final_amount,
            status='pending'
        )
        db.session.add(payment)
        db.session.commit()

        return redirect(checkout_session.url, code=303)
    except Exception as e:
        return jsonify(error=str(e)), 500

@routes.route('/payment-success')
@login_required
def payment_success():
    session_id = request.args.get('session_id')
    return render_template('payment/success.html', session_id=session_id)

@routes.route('/payment-cancel')
@login_required
def payment_cancel():
    return render_template('payment/cancel.html')

@routes.route('/stripe-webhook', methods=['POST'])
def stripe_webhook():
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')
    endpoint_secret = os.getenv('STRIPE_WEBHOOK_SECRET')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        return 'Invalid payload', 400
    except stripe.error.SignatureVerificationError as e:
        return 'Invalid signature', 400

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        handle_checkout_session(session)

    return 'Success', 200

def handle_checkout_session(session):
    order_id = session.get('metadata').get('order_id')
    order = Order.query.get(order_id)
    if order:
        order.status = OrderStatus.PAID
        
        payment = Payment.query.filter_by(stripe_session_id=session.id).first()
        if payment:
            payment.status = 'succeeded'
            payment.stripe_payment_intent = session.payment_intent
            
        # Clear user cart upon successful payment
        Cart.query.filter_by(user_id=order.user_id).delete()
        
        db.session.commit()
        
        # Trigger Email Notification (Placeholder)
        print(f"Order {order.id} marked as PAID. Notification sent to user {order.user_id}.")
