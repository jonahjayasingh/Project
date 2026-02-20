from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta
from members.models import Member
from memberships.models import MemberMembership, MembershipPlan
from attendance.models import Attendance
from payments.models import Payment
from classes.models import ClassBooking, FitnessClass
from trainers.models import Trainer

from django.contrib.auth.forms import AuthenticationForm


def landing_page(request):
    """
    Landing page for non-authenticated users
    """
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    
    # Get some stats for the landing page
    total_members = Member.objects.filter(status='active').count()
    total_classes = FitnessClass.objects.count()
    total_trainers = Trainer.objects.filter(is_available=True).count()
    
    context = {
        'total_members': total_members,
        'total_classes': total_classes,
        'total_trainers': total_trainers,
        'login_form': AuthenticationForm(),
    }
    
    return render(request, 'home.html', context)


@login_required
def home(request):
    """
    Main dashboard - redirects based on user role
    """
    user = request.user
    
    if user.is_admin() or user.is_staff_member():
        return redirect('dashboard:admin_dashboard')
    elif user.is_trainer():
        return redirect('dashboard:trainer_dashboard')
    else:
        return redirect('dashboard:member_dashboard')


@login_required
def admin_dashboard(request):
    """
    Admin dashboard with analytics
    """
    # Check if user has admin access
    if not (request.user.is_admin() or request.user.is_staff_member()):
        return redirect('dashboard:member_dashboard')
    
    # Get current date and date ranges
    today = timezone.now().date()
    this_month_start = today.replace(day=1)
    last_month_start = (this_month_start - timedelta(days=1)).replace(day=1)
    
    # Member statistics
    total_members = Member.objects.count()
    active_members = Member.objects.filter(status='active').count()
    inactive_members = Member.objects.filter(status='inactive').count()
    frozen_members = Member.objects.filter(status='frozen').count()
    
    # Membership statistics
    active_memberships = MemberMembership.objects.filter(status='active').count()
    expiring_soon = MemberMembership.objects.filter(
        status='active',
        end_date__lte=today + timedelta(days=7),
        end_date__gte=today
    ).count()
    
    # Revenue statistics
    this_month_revenue = Payment.objects.filter(
        payment_date__gte=this_month_start,
        status='completed'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    last_month_revenue = Payment.objects.filter(
        payment_date__gte=last_month_start,
        payment_date__lt=this_month_start,
        status='completed'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Attendance statistics
    today_attendance = Attendance.objects.filter(date=today).count()
    this_week_attendance = Attendance.objects.filter(
        date__gte=today - timedelta(days=7)
    ).count()
    
    # Class statistics
    popular_classes = FitnessClass.objects.annotate(
        booking_count=Count('schedules__bookings')
    ).order_by('-booking_count')[:5]
    
    # Recent payments
    recent_payments = Payment.objects.select_related('member__user').order_by('-payment_date')[:10]
    
    # Pending dues
    pending_payments = Payment.objects.filter(status='pending').select_related('member__user')
    
    context = {
        'total_members': total_members,
        'active_members': active_members,
        'inactive_members': inactive_members,
        'frozen_members': frozen_members,
        'active_memberships': active_memberships,
        'expiring_soon': expiring_soon,
        'this_month_revenue': this_month_revenue,
        'last_month_revenue': last_month_revenue,
        'today_attendance': today_attendance,
        'this_week_attendance': this_week_attendance,
        'popular_classes': popular_classes,
        'recent_payments': recent_payments,
        'pending_payments': pending_payments,
    }
    
    return render(request, 'dashboard/admin_dashboard.html', context)


@login_required
def member_dashboard(request):
    """
    Member dashboard
    """
    try:
        member = request.user.member_profile
    except:
        # If user doesn't have a member profile, show basic info
        return render(request, 'dashboard/member_dashboard.html', {
            'no_profile': True
        })
    
    # Get active membership
    active_membership = member.get_active_membership()
    
    # Get recent attendance
    recent_attendance = Attendance.objects.filter(
        member=member
    ).order_by('-check_in_time')[:10]
    
    # Get upcoming class bookings
    upcoming_classes = ClassBooking.objects.filter(
        member=member,
        status__in=['confirmed', 'waitlist']
    ).select_related('schedule__fitness_class', 'schedule__trainer__user').order_by('schedule__day_of_week', 'schedule__start_time')[:5]
    
    # Get payment history
    recent_payments = Payment.objects.filter(
        member=member
    ).order_by('-payment_date')[:5]
    
    # Get pending payments
    pending_payments = Payment.objects.filter(
        member=member,
        status='pending'
    )
    
    context = {
        'member': member,
        'active_membership': active_membership,
        'recent_attendance': recent_attendance,
        'upcoming_classes': upcoming_classes,
        'recent_payments': recent_payments,
        'pending_payments': pending_payments,
    }
    
    return render(request, 'dashboard/member_dashboard.html', context)


@login_required
def trainer_dashboard(request):
    """
    Trainer dashboard
    """
    if not request.user.is_trainer():
        return redirect('dashboard:home')
    
    try:
        trainer = request.user.trainer_profile
    except:
        return render(request, 'dashboard/trainer_dashboard.html', {
            'no_profile': True
        })
    
    # Get assigned members
    assigned_members = trainer.member_assignments.filter(
        status='active'
    ).select_related('member__user')
    
    # Get scheduled classes
    scheduled_classes = trainer.class_schedules.filter(
        is_active=True
    ).select_related('fitness_class').order_by('day_of_week', 'start_time')
    
    # Get class bookings for today
    today = timezone.now().date()
    today_weekday = today.weekday()
    
    today_classes = scheduled_classes.filter(day_of_week=today_weekday)
    print(today_classes[0].fitness_class.capacity)
    context = {
        'trainer': trainer,
        'assigned_members': assigned_members,
        'scheduled_classes': scheduled_classes,
        'today_classes': today_classes,
    }
    
    return render(request, 'dashboard/trainer_dashboard.html', context)
