from functools import wraps
from flask import session, redirect, url_for, flash
from models import UserType


def login_required(f):
    """Decorator to require login for a route"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def seller_required(f):
    """Decorator to require seller access for a route"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('auth.login'))
        
        if session.get('user_type') != UserType.SELLER.value:
            # Check if user has seller profile
            from models import User
            user = User.query.get(session['user_id'])
            if not user or not hasattr(user, 'seller_profile') or not user.seller_profile:
                flash('You must be a seller to access this page.', 'error')
                return redirect(url_for('seller.become_seller'))
        
        return f(*args, **kwargs)
    return decorated_function


def customer_required(f):
    """Decorator to require customer access (just logged in)"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Decorator to require admin access for a route"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('auth.login'))
        
        if session.get('user_type') != UserType.ADMIN.value:
            flash('You must be an administrator to access this page.', 'error')
            return redirect(url_for('index'))
        
        return f(*args, **kwargs)
    return decorated_function
