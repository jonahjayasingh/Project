from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from .models import MembershipRequest, TrainerRequest
from .forms import MembershipRequestForm, TrainerRequestForm
from memberships.models import MembershipPlan
from trainers.models import Trainer


def membership_plans_view(request):
    """
    Display all available membership plans
    """
    plans = MembershipPlan.objects.filter(is_active=True).order_by('duration_months', 'price')
    context = {
        'plans': plans,
        'page_title': 'Membership Plans'
    }
    return render(request, 'requests/membership_plans.html', context)


def request_membership_view(request, plan_id=None):
    """
    Handle membership request form submission
    """
    selected_plan = None
    if plan_id:
        selected_plan = get_object_or_404(MembershipPlan, id=plan_id, is_active=True)
    
    if request.method == 'POST':
        form = MembershipRequestForm(request.POST)
        if form.is_valid():
            membership_request = form.save()
            
            # Send email notification to admin
            try:
                send_mail(
                    subject=f'New Membership Request - {membership_request.get_full_name()}',
                    message=f'''
New membership request received:

Name: {membership_request.get_full_name()}
Email: {membership_request.email}
Phone: {membership_request.phone_number}
Selected Plan: {membership_request.selected_plan.name}

Please review and process this request in the admin panel.
                    ''',
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[settings.EMAIL_RECIVER],
                    fail_silently=True,
                )
            except:
                pass
            
            messages.success(request, 'Your membership request has been submitted successfully! We will contact you soon.')
            return redirect('requests:membership_request_success')
    else:
        initial_data = {}
        if selected_plan:
            initial_data['selected_plan'] = selected_plan
        form = MembershipRequestForm(initial=initial_data)
    
    context = {
        'form': form,
        'selected_plan': selected_plan,
        'page_title': 'Request Membership'
    }
    return render(request, 'requests/request_membership.html', context)


def membership_request_success_view(request):
    """
    Success page after membership request submission
    """
    return render(request, 'requests/membership_request_success.html', {'page_title': 'Request Submitted'})


@login_required
def trainers_list_view(request):
    """
    Display all available trainers
    """
    trainers = Trainer.objects.filter(is_available=True).select_related('user')
    context = {
        'trainers': trainers,
        'page_title': 'Our Trainers'
    }
    return render(request, 'requests/trainers_list.html', context)


@login_required
def request_trainer_view(request, trainer_id=None):
    """
    Handle trainer request form submission
    """
    # Check if user has a member profile
    if not hasattr(request.user, 'member_profile'):
        messages.error(request, 'You must be a registered member to request a trainer.')
        return redirect('dashboard:home')
    
    member = request.user.member_profile
    preferred_trainer = None
    
    if trainer_id:
        preferred_trainer = get_object_or_404(Trainer, id=trainer_id, is_available=True)
    
    if request.method == 'POST':
        form = TrainerRequestForm(request.POST)
        if form.is_valid():
            trainer_request = form.save(commit=False)
            trainer_request.member = member
            trainer_request.save()
            
            # Send email notification to admin
            try:
                send_mail(
                    subject=f'New Trainer Request - {member.user.get_full_name()}',
                    message=f'''
New trainer request received:

Member: {member.user.get_full_name()}
Email: {member.user.email}
Preferred Specialization: {trainer_request.get_preferred_specialization_display()}
Sessions per Week: {trainer_request.sessions_per_week}

Please review and process this request in the admin panel.
                    ''',
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[settings.EMAIL_RECIVER],
                    fail_silently=True,
                )
            except:
                pass
            
            messages.success(request, 'Your trainer request has been submitted successfully! We will assign a trainer soon.')
            return redirect('requests:trainer_request_success')
    else:
        initial_data = {}
        if preferred_trainer:
            initial_data['preferred_trainer'] = preferred_trainer
            initial_data['preferred_specialization'] = preferred_trainer.specialization
        form = TrainerRequestForm(initial=initial_data)
    
    context = {
        'form': form,
        'preferred_trainer': preferred_trainer,
        'page_title': 'Request Personal Trainer'
    }
    return render(request, 'requests/request_trainer.html', context)


@login_required
def trainer_request_success_view(request):
    """
    Success page after trainer request submission
    """
    return render(request, 'requests/trainer_request_success.html', {'page_title': 'Request Submitted'})


@login_required
def my_requests_view(request):
    """
    View member's own requests
    """
    if not hasattr(request.user, 'member_profile'):
        messages.error(request, 'You must be a registered member to view requests.')
        return redirect('dashboard:home')
    
    member = request.user.member_profile
    trainer_requests = TrainerRequest.objects.filter(member=member).order_by('-created_at')
    
    context = {
        'trainer_requests': trainer_requests,
        'page_title': 'My Requests'
    }
    return render(request, 'requests/my_requests.html', context)
