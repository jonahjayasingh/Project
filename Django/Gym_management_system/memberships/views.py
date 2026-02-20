from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q, Count
from django.core.paginator import Paginator
from .models import MembershipPlan, MemberMembership
from .forms import MembershipPlanForm, MemberMembershipForm, FreezeForm


def is_admin_or_staff(user):
    """Check if user is admin or staff"""
    return user.is_authenticated and (user.is_admin() or user.is_staff_member())


# Membership Plan Views
@login_required
@user_passes_test(is_admin_or_staff)
def plan_list(request):
    """List all membership plans"""
    plans = MembershipPlan.objects.annotate(
        active_subscriptions=Count('subscriptions', filter=Q(subscriptions__status='active'))
    ).all()
    
    context = {'plans': plans}
    return render(request, 'memberships/plan_list.html', context)


@login_required
@user_passes_test(is_admin_or_staff)
def plan_detail(request, pk):
    """View plan details"""
    plan = get_object_or_404(MembershipPlan, pk=pk)
    subscriptions = plan.subscriptions.select_related('member__user').all()[:20]
    
    context = {
        'plan': plan,
        'subscriptions': subscriptions,
    }
    return render(request, 'memberships/plan_detail.html', context)


@login_required
@user_passes_test(is_admin_or_staff)
def plan_create(request):
    """Create new membership plan"""
    if request.method == 'POST':
        form = MembershipPlanForm(request.POST)
        
        if form.is_valid():
            plan = form.save()
            messages.success(request, f'Plan "{plan.name}" created successfully!')
            return redirect('memberships:plan_detail', pk=plan.pk)
    else:
        form = MembershipPlanForm()
    
    context = {
        'form': form,
        'title': 'Create Membership Plan',
    }
    return render(request, 'memberships/plan_form.html', context)


@login_required
@user_passes_test(is_admin_or_staff)
def plan_edit(request, pk):
    """Edit membership plan"""
    plan = get_object_or_404(MembershipPlan, pk=pk)
    
    if request.method == 'POST':
        form = MembershipPlanForm(request.POST, instance=plan)
        
        if form.is_valid():
            form.save()
            messages.success(request, f'Plan "{plan.name}" updated successfully!')
            return redirect('memberships:plan_detail', pk=plan.pk)
    else:
        form = MembershipPlanForm(instance=plan)
    
    context = {
        'form': form,
        'plan': plan,
        'title': 'Edit Membership Plan',
    }
    return render(request, 'memberships/plan_form.html', context)


@login_required
@user_passes_test(is_admin_or_staff)
def plan_delete(request, pk):
    """Delete membership plan"""
    plan = get_object_or_404(MembershipPlan, pk=pk)
    
    if request.method == 'POST':
        plan_name = plan.name
        plan.delete()
        messages.success(request, f'Plan "{plan_name}" deleted successfully!')
        return redirect('memberships:plan_list')
    
    context = {'plan': plan}
    return render(request, 'memberships/plan_confirm_delete.html', context)


# Member Membership Views
@login_required
@user_passes_test(is_admin_or_staff)
def membership_list(request):
    """List all member memberships"""
    memberships = MemberMembership.objects.select_related('member__user', 'plan').all()
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        memberships = memberships.filter(status=status_filter)
    
    # Pagination
    paginator = Paginator(memberships, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'status_choices': MemberMembership.STATUS_CHOICES,
    }
    return render(request, 'memberships/membership_list.html', context)


@login_required
@user_passes_test(is_admin_or_staff)
def membership_create(request):
    """Assign plan to member"""
    if request.method == 'POST':
        form = MemberMembershipForm(request.POST)
        
        if form.is_valid():
            membership = form.save()
            messages.success(request, f'Membership assigned to {membership.member.user.get_full_name()}!')
            return redirect('members:member_detail', pk=membership.member.pk)
    else:
        form = MemberMembershipForm()
    
    context = {
        'form': form,
        'title': 'Assign Membership',
    }
    return render(request, 'memberships/membership_form.html', context)


@login_required
@user_passes_test(is_admin_or_staff)
def membership_edit(request, pk):
    """Edit membership"""
    membership = get_object_or_404(MemberMembership, pk=pk)
    
    if request.method == 'POST':
        form = MemberMembershipForm(request.POST, instance=membership)
        
        if form.is_valid():
            form.save()
            messages.success(request, 'Membership updated successfully!')
            return redirect('members:member_detail', pk=membership.member.pk)
    else:
        form = MemberMembershipForm(instance=membership)
    
    context = {
        'form': form,
        'membership': membership,
        'title': 'Edit Membership',
    }
    return render(request, 'memberships/membership_form.html', context)


@login_required
@user_passes_test(is_admin_or_staff)
def membership_freeze(request, pk):
    """Freeze membership"""
    membership = get_object_or_404(MemberMembership, pk=pk)
    
    if request.method == 'POST':
        form = FreezeForm(request.POST)
        
        if form.is_valid():
            freeze_days = form.cleaned_data['freeze_days']
            membership.freeze_membership(freeze_days)
            messages.success(request, f'Membership frozen for {freeze_days} days!')
            return redirect('members:member_detail', pk=membership.member.pk)
    else:
        form = FreezeForm()
    
    context = {
        'form': form,
        'membership': membership,
    }
    return render(request, 'memberships/freeze_form.html', context)


@login_required
@user_passes_test(is_admin_or_staff)
def membership_unfreeze(request, pk):
    """Unfreeze membership"""
    membership = get_object_or_404(MemberMembership, pk=pk)
    
    if request.method == 'POST':
        membership.unfreeze_membership()
        messages.success(request, 'Membership unfrozen successfully!')
        return redirect('members:member_detail', pk=membership.member.pk)
    
    context = {'membership': membership}
    return render(request, 'memberships/unfreeze_confirm.html', context)
