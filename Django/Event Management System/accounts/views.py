from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegistrationForm, UserLoginForm
from .decorators import admin_required, client_required

def register_view(request):
    """
    User registration view.
    """
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Account created successfully! Welcome, {user.username}.')
            login(request, user)
            return redirect('accounts:dashboard')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """
    User login view with role-based dashboard redirect.
    """
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.username}!')
                return redirect('accounts:dashboard')
    else:
        form = UserLoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    """
    User logout view.
    """
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('accounts:login')


@login_required
def dashboard_view(request):
    """
    Role-based dashboard redirect.
    Admins see admin dashboard, clients see client dashboard.
    """
    if request.user.is_admin():
        return redirect('accounts:admin_dashboard')
    else:
        return redirect('accounts:client_dashboard')


@admin_required
def admin_dashboard_view(request):
    """
    Admin dashboard view.
    """
    from events.models import Event
    from food.models import MenuItem
    from services.models import Service

    events = Event.objects.all()
    menu_items = MenuItem.objects.all()
    services = Service.objects.all()

    context = {
        'events_count': events.count(),
        'menu_items_count': menu_items.count(),
        'services_count': services.count(),
        'recent_events': events.order_by('-created_at')[:5],
    }
    return render(request, 'accounts/admin_dashboard.html', context)


@client_required
def client_dashboard_view(request):
    """
    Client dashboard view.
    """
    from events.models import Event
    
    events = Event.objects.filter(client=request.user)
    
    context = {
        'events_count': events.count(),
        'recent_events': events.order_by('-created_at')[:5],
    }
    return render(request, 'accounts/client_dashboard.html', context)
