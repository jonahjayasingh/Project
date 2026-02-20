from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm

def home_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'home.html')

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            if user.role in ['ngo', 'volunteer']:
                user.is_approved = False
            user.save()
            login(request, user)
            messages.success(request, f"Welcome, {user.username}! Your account has been created successfully.")
            return redirect('dashboard')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

def pending_approval_view(request):
    return render(request, 'accounts/pending_approval.html')

@login_required
def dashboard_redirect(request):
    user = request.user
    if not user.is_approved:
        return redirect('pending_approval')
        
    role = user.role
    if role == 'donor':
        return redirect('donor_dashboard')
    elif role == 'ngo':
        return redirect('ngo_dashboard')
    elif role == 'volunteer':
        return redirect('volunteer_dashboard')
    elif role == 'admin':
        return redirect('admin_dashboard')
    return redirect('login')

@login_required
def update_location(request):
    """Update user location (for volunteers and NGOs)"""
    if request.method == 'POST':
        address = request.POST.get('address')
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        
        user = request.user
        user.address = address
        user.latitude = latitude if latitude else None
        user.longitude = longitude if longitude else None
        user.save()
        
        messages.success(request, "Your location has been updated successfully!")
        return redirect('dashboard')
    
    return render(request, 'accounts/update_location.html')
