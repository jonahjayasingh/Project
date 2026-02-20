from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .models import CustomUser
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth import update_session_auth_hash


def login_view(request):
    """
    Handle user login (POST from home page)
    """
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
                
                # Redirect based on role
                if user.is_admin() or user.is_staff_member():
                    return redirect('dashboard:admin_dashboard')
                elif user.is_trainer():
                    return redirect('dashboard:trainer_dashboard')
                else:
                    return redirect('dashboard:member_dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    
    # If GET request or failed POST, redirect to home
    return redirect('home')


def member_login(request):
    """
    Handle member login with role validation
    """
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                # Check if user is a member
                if user.is_member():
                    login(request, user)
                    messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
                    return redirect('dashboard:member_dashboard')
                else:
                    messages.error(request, 'This account is not registered as a member. Please use the appropriate login page.')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'accounts/member_login.html')


def trainer_login(request):
    """
    Handle trainer login with role validation
    """
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                # Check if user is a trainer
                if user.is_trainer():
                    login(request, user)
                    messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
                    return redirect('dashboard:trainer_dashboard')
                elif user.is_admin() or user.is_staff_member():
                    # Allow admin/staff to access trainer dashboard
                    login(request, user)
                    messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
                    return redirect('dashboard:admin_dashboard')
                else:
                    messages.error(request, 'This account is not registered as a trainer. Please use the member login page.')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'accounts/trainer_login.html')


def admin_login(request):
    """
    Handle admin login with role validation
    """
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                # Check if user is admin or staff
                if user.is_admin() or user.is_staff_member():
                    login(request, user)
                    messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
                    return redirect('dashboard:admin_dashboard')
                else:
                    messages.error(request, 'Access denied. This portal is for administrators only. Please use the appropriate login page.')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'accounts/admin_login.html')



@login_required
def logout_view(request):
    """
    Handle user logout
    """
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('accounts:login')


@login_required
def profile_view(request):
    """
    Display and update user profile
    """
    from .forms import UserEditForm
    from members.forms import MemberProfileForm
    from trainers.forms import TrainerProfileForm
    
    user = request.user
    member_profile = None
    trainer_profile = None
    
    # Get member or trainer profile if exists
    if user.is_member():
        try:
            member_profile = user.member_profile
        except:
            pass
    elif user.is_trainer():
        try:
            trainer_profile = user.trainer_profile
        except:
            pass
    
    if request.method == 'POST':
        user_form = UserEditForm(request.POST, request.FILES, instance=user)
        
        # Initialize profile forms based on role
        member_form = None
        trainer_form = None
        
        if member_profile:
            member_form = MemberProfileForm(request.POST, instance=member_profile)
        elif trainer_profile:
            trainer_form = TrainerProfileForm(request.POST, instance=trainer_profile)
        
        # Validate all applicable forms
        forms_valid = user_form.is_valid()
        if member_form:
            forms_valid = forms_valid and member_form.is_valid()
        if trainer_form:
            forms_valid = forms_valid and trainer_form.is_valid()
        
        if forms_valid:
            user_form.save()
            if member_form:
                member_form.save()
            if trainer_form:
                trainer_form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        user_form = UserEditForm(instance=user)
        member_form = MemberProfileForm(instance=member_profile) if member_profile else None
        trainer_form = TrainerProfileForm(instance=trainer_profile) if trainer_profile else None
    
    context = {
        'user': user,
        'user_form': user_form,
        'member_form': member_form,
        'trainer_form': trainer_form,
        'member_profile': member_profile,
        'trainer_profile': trainer_profile,
    }
    
    return render(request, 'accounts/profile.html', context)


@login_required
def change_password(request):
    """
    Handle password change
    """
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Keep user logged in
            messages.success(request, 'Your password was successfully updated!')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'accounts/change_password.html', {'form': form})
