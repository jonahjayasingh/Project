from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.core.mail import send_mail
from django.conf import settings
from .models import Trainer, TrainerAvailability, TrainerMemberAssignment
from .forms import (TrainerRegistrationForm, TrainerUserEditForm, TrainerProfileForm,
                    TrainerAvailabilityForm, TrainerAssignmentForm)


def is_admin_or_staff(user):
    """Check if user is admin or staff"""
    return user.is_authenticated and (user.is_admin() or user.is_staff_member())


@login_required
@user_passes_test(is_admin_or_staff)
def trainer_list(request):
    """List all trainers with search and filter"""
    trainers = Trainer.objects.select_related('user').all()
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        trainers = trainers.filter(
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(user__email__icontains=search_query) |
            Q(specialization__icontains=search_query)
        )
    
    # Filter by specialization
    specialization_filter = request.GET.get('specialization', '')
    if specialization_filter:
        trainers = trainers.filter(specialization=specialization_filter)
    
    # Filter by availability
    availability_filter = request.GET.get('availability', '')
    if availability_filter:
        trainers = trainers.filter(is_available=(availability_filter == 'true'))
    
    # Annotate with assignment count
    trainers = trainers.annotate(active_assignments=Count('member_assignments', filter=Q(member_assignments__status='active')))
    
    # Pagination
    paginator = Paginator(trainers, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'specialization_filter': specialization_filter,
        'availability_filter': availability_filter,
        'specialization_choices': Trainer.SPECIALIZATION_CHOICES,
    }
    return render(request, 'trainers/trainer_list.html', context)


@login_required
@user_passes_test(is_admin_or_staff)
def trainer_detail(request, pk):
    """View trainer details"""
    trainer = get_object_or_404(Trainer.objects.select_related('user'), pk=pk)
    
    # Get trainer's availability
    availability = trainer.availability.filter(is_active=True).order_by('day_of_week', 'start_time')
    
    # Get active assignments
    active_assignments = trainer.member_assignments.filter(status='active').select_related('member__user')
    
    # Get class schedules
    class_schedules = trainer.class_schedules.filter(is_active=True).select_related('fitness_class').order_by('day_of_week', 'start_time')
    
    # Get assignment history
    assignment_history = trainer.member_assignments.exclude(status='active').select_related('member__user').order_by('-start_date')[:10]
    
    context = {
        'trainer': trainer,
        'availability': availability,
        'active_assignments': active_assignments,
        'class_schedules': class_schedules,
        'assignment_history': assignment_history,
    }
    return render(request, 'trainers/trainer_detail.html', context)


@login_required
@user_passes_test(is_admin_or_staff)
def trainer_create(request):
    """Create a new trainer"""
    if request.method == 'POST':
        user_form = TrainerRegistrationForm(request.POST, request.FILES)
        profile_form = TrainerProfileForm(request.POST)
        
        if user_form.is_valid() and profile_form.is_valid():
            # Capture the plain password before it gets hashed
            plain_password = user_form.cleaned_data.get('password1')
            
            # Create user
            user = user_form.save()
            
            # Create trainer profile
            trainer = profile_form.save(commit=False)
            trainer.user = user
            trainer.save()
            
            # Send welcome email to the new trainer
            try:
                send_mail(
                    subject='Welcome to Our Gym Team!',
                    message=f'''
Dear {user.get_full_name()},

Welcome to our Gym Management System! Your trainer account has been successfully created.

Your Login Details:
-------------------
Username: {user.username}
Password: {plain_password}
Email: {user.email}

Login URL: http://localhost:8000/

IMPORTANT: Please keep this password safe and consider changing it after your first login.

Your Profile:
-------------
Specialization: {trainer.get_specialization_display()}
Experience: {trainer.experience_years} years
Hourly Rate: ${trainer.hourly_rate}

As a trainer, you can:
- Log in to the system using the credentials above
- View and manage your class schedules
- Track your assigned members
- Update your availability
- View your dashboard and statistics

If you have any questions or need assistance, please don't hesitate to contact us.

Best regards,
Gym Management Team
                    ''',
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[user.email],
                    fail_silently=True,
                )
            except Exception as e:
                print(f"Error sending welcome email: {e}")
            
            # Send notification to admin
            try:
                send_mail(
                    subject=f'New Trainer Registered - {user.get_full_name()}',
                    message=f'''
New trainer has been registered in the system:

Trainer Details:
---------------
Name: {user.get_full_name()}
Username: {user.username}
Email: {user.email}
Phone: {user.phone_number}
Date of Birth: {user.date_of_birth}
Gender: {user.get_gender_display() if user.gender else 'Not specified'}

Professional Information:
------------------------
Specialization: {trainer.get_specialization_display()}
Experience: {trainer.experience_years} years
Hourly Rate: ${trainer.hourly_rate}
Certifications: {trainer.certifications if trainer.certifications else 'None provided'}
Availability Status: {'Available' if trainer.is_available else 'Not Available'}

Registered by: {request.user.get_full_name()}
Registration Date: {trainer.hire_date}

You can view the full trainer profile in the admin panel.
                    ''',
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[settings.EMAIL_RECIVER],
                    fail_silently=True,
                )
            except Exception as e:
                print(f"Error sending admin notification: {e}")
            
            messages.success(request, f'Trainer {user.get_full_name()} created successfully! Welcome email sent.')
            return redirect('trainers:trainer_detail', pk=trainer.pk)
    else:
        user_form = TrainerRegistrationForm()
        profile_form = TrainerProfileForm()
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'title': 'Add New Trainer',
    }
    return render(request, 'trainers/trainer_form.html', context)


@login_required
@user_passes_test(is_admin_or_staff)
def trainer_edit(request, pk):
    """Edit trainer information"""
    trainer = get_object_or_404(Trainer, pk=pk)
    
    if request.method == 'POST':
        user_form = TrainerUserEditForm(request.POST, request.FILES, instance=trainer.user)
        profile_form = TrainerProfileForm(request.POST, instance=trainer)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            
            messages.success(request, f'Trainer {trainer.user.get_full_name()} updated successfully!')
            return redirect('trainers:trainer_detail', pk=trainer.pk)
    else:
        user_form = TrainerUserEditForm(instance=trainer.user)
        profile_form = TrainerProfileForm(instance=trainer)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'trainer': trainer,
        'title': 'Edit Trainer',
    }
    return render(request, 'trainers/trainer_form.html', context)


@login_required
@user_passes_test(is_admin_or_staff)
def trainer_delete(request, pk):
    """Delete a trainer"""
    trainer = get_object_or_404(Trainer, pk=pk)
    
    if request.method == 'POST':
        trainer_name = trainer.user.get_full_name()
        user = trainer.user
        trainer.delete()
        user.delete()
        
        messages.success(request, f'Trainer {trainer_name} deleted successfully!')
        return redirect('trainers:trainer_list')
    
    context = {'trainer': trainer}
    return render(request, 'trainers/trainer_confirm_delete.html', context)


@login_required
@user_passes_test(is_admin_or_staff)
def availability_create(request, trainer_pk):
    """Add availability slot for trainer"""
    trainer = get_object_or_404(Trainer, pk=trainer_pk)
    
    if request.method == 'POST':
        form = TrainerAvailabilityForm(request.POST)
        
        if form.is_valid():
            availability = form.save(commit=False)
            availability.trainer = trainer
            availability.save()
            
            messages.success(request, 'Availability slot added successfully!')
            return redirect('trainers:trainer_detail', pk=trainer.pk)
    else:
        form = TrainerAvailabilityForm()
    
    context = {
        'form': form,
        'trainer': trainer,
        'title': 'Add Availability',
    }
    return render(request, 'trainers/availability_form.html', context)


@login_required
@user_passes_test(is_admin_or_staff)
def availability_delete(request, pk):
    """Delete availability slot"""
    availability = get_object_or_404(TrainerAvailability, pk=pk)
    trainer = availability.trainer
    
    if request.method == 'POST':
        availability.delete()
        messages.success(request, 'Availability slot deleted successfully!')
        return redirect('trainers:trainer_detail', pk=trainer.pk)
    
    context = {
        'availability': availability,
        'trainer': trainer,
    }
    return render(request, 'trainers/availability_confirm_delete.html', context)


@login_required
@user_passes_test(is_admin_or_staff)
def assignment_create(request):
    """Create trainer-member assignment"""
    if request.method == 'POST':
        form = TrainerAssignmentForm(request.POST)
        
        if form.is_valid():
            assignment = form.save()
            messages.success(request, f'Trainer {assignment.trainer.user.get_full_name()} assigned to {assignment.member.user.get_full_name()}!')
            return redirect('trainers:trainer_detail', pk=assignment.trainer.pk)
    else:
        form = TrainerAssignmentForm()
    
    context = {
        'form': form,
        'title': 'Assign Trainer to Member',
    }
    return render(request, 'trainers/assignment_form.html', context)


@login_required
@user_passes_test(is_admin_or_staff)
def assignment_update(request, pk):
    """Update trainer-member assignment"""
    assignment = get_object_or_404(TrainerMemberAssignment, pk=pk)
    
    if request.method == 'POST':
        form = TrainerAssignmentForm(request.POST, instance=assignment)
        
        if form.is_valid():
            form.save()
            messages.success(request, 'Assignment updated successfully!')
            return redirect('trainers:trainer_detail', pk=assignment.trainer.pk)
    else:
        form = TrainerAssignmentForm(instance=assignment)
    
    context = {
        'form': form,
        'assignment': assignment,
        'title': 'Update Assignment',
    }
    return render(request, 'trainers/assignment_form.html', context)
