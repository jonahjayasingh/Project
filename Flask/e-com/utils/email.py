from flask_mail import Message
from flask import render_template, current_app
# Assume 'mail' is initialized in app.py and we import it here if needed, 
# or use a proxy. For blueprint logic, we'll use current_app.extensions['mail']

def send_email(subject, recipient, template, **kwargs):
    """Utility to send HTML emails"""
    from app import mail
    try:
        msg = Message(
            subject,
            recipients=[recipient],
            sender=current_app.config.get('MAIL_DEFAULT_SENDER')
        )
        msg.html = render_template(template, **kwargs)
        mail.send(msg)
    except Exception as e:
        # Logistic: Log error but don't crash the request
        print(f"FAILED TO SEND EMAIL: {str(e)}")

def send_order_confirmation(user, order):
    send_email(
        f"Order Confirmation #ORD-{order.id}",
        user.username if "@" in user.username else "customer@example.com", # Fallback for dev usernames
        "emails/order_confirmation.html",
        user=user,
        order=order
    )

def send_shipping_update(user, order):
    send_email(
        f"Shipping Update: Order #ORD-{order.id}",
        user.username if "@" in user.username else "customer@example.com",
        "emails/shipping_update.html",
        user=user,
        order=order
    )
