from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def admin_required(view_func):
    """
    Decorator to restrict access to admin users only.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please login to access this page.')
            return redirect('accounts:login')
        
        if not request.user.is_admin():
            messages.error(request, 'Access denied. Admin privileges required.')
            return redirect('accounts:dashboard')
        
        return view_func(request, *args, **kwargs)
    return wrapper


def client_required(view_func):
    """
    Decorator to restrict access to client users only.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please login to access this page.')
            return redirect('accounts:login')
        
        if not request.user.is_client():
            messages.error(request, 'Access denied. Client privileges required.')
            return redirect('accounts:dashboard')
        
        return view_func(request, *args, **kwargs)
    return wrapper
