from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.core.mail import send_mail
from django.conf import settings
from .models import Member
from .forms import MemberProfileForm
from accounts.forms import MemberRegistrationForm, UserEditForm
from accounts.models import CustomUser


def is_admin_or_staff(user):
    """Check if user is admin or staff"""
    return user.is_authenticated and (user.is_admin() or user.is_staff_member())


@login_required
@user_passes_test(is_admin_or_staff)
def member_list(request):
    """List all members with search and filter"""
    members = Member.objects.select_related('user').all()
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        members = members.filter(
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(user__email__icontains=search_query) |
            Q(user__phone_number__icontains=search_query)
        )
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        members = members.filter(status=status_filter)
    
    # Pagination
    paginator = Paginator(members, 10)  # 10 members per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'status_choices': Member.STATUS_CHOICES,
    }
    return render(request, 'members/member_list.html', context)


@login_required
@user_passes_test(is_admin_or_staff)
def member_detail(request, pk):
    """View member details"""
    member = get_object_or_404(Member.objects.select_related('user'), pk=pk)
    
    # Get member's memberships
    memberships = member.memberships.all().order_by('-start_date')
    
    # Get recent attendance
    recent_attendance = member.attendance_records.all().order_by('-check_in_time')[:10]
    
    # Get payments
    payments = member.payments.all().order_by('-payment_date')[:10]
    
    # Get class bookings
    class_bookings = member.class_bookings.select_related(
        'schedule__fitness_class', 'schedule__trainer__user'
    ).all()[:10]
    
    context = {
        'member': member,
        'memberships': memberships,
        'recent_attendance': recent_attendance,
        'payments': payments,
        'class_bookings': class_bookings,
    }
    return render(request, 'members/member_detail.html', context)


@login_required
@user_passes_test(is_admin_or_staff)
def member_create(request):
    """Create a new member"""
    if request.method == 'POST':
        user_form = MemberRegistrationForm(request.POST, request.FILES)
        profile_form = MemberProfileForm(request.POST)
        
        if user_form.is_valid() and profile_form.is_valid():
            # Capture the plain password before it gets hashed
            plain_password = user_form.cleaned_data.get('password1')
            
            # Create user
            user = user_form.save()
            
            # Create member profile
            member = profile_form.save(commit=False)
            member.user = user
            member.save()
            
            # Send welcome email to the new member
            try:
                send_mail(
                    subject='Welcome to Our Gym!',
                    message=f'''
Dear {user.get_full_name()},

Welcome to our Gym Management System! Your account has been successfully created.

Your Login Details:
-------------------
Username: {user.username}
Password: {plain_password}
Email: {user.email}

Login URL: http://localhost:8000/

IMPORTANT: Please keep this password safe and consider changing it after your first login.

What's Next?
- Log in to the system using the credentials above
- Complete your profile information
- Check out our available classes
- View your membership details
- Track your attendance

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
                    subject=f'New Member Registered - {user.get_full_name()}',
                    message=f'''
New member has been registered in the system:

Member Details:
--------------
Name: {user.get_full_name()}
Username: {user.username}
Email: {user.email}
Phone: {user.phone_number}
Date of Birth: {user.date_of_birth}
Gender: {user.get_gender_display() if user.gender else 'Not specified'}

Health Information:
------------------
Blood Group: {member.blood_group if member.blood_group else 'Not specified'}
Height: {member.height} cm
Weight: {member.weight} kg
Emergency Contact: {member.emergency_contact_name} ({member.emergency_contact_phone})

Registered by: {request.user.get_full_name()}
Registration Date: {member.join_date}

You can view the full member profile in the admin panel.
                    ''',
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[settings.EMAIL_RECIVER],
                    fail_silently=True,
                )
            except Exception as e:
                print(f"Error sending admin notification: {e}")
            
            messages.success(request, f'Member {user.get_full_name()} created successfully! Welcome email sent with login credentials.')
            return redirect('members:member_detail', pk=member.pk)
    else:
        user_form = MemberRegistrationForm()
        profile_form = MemberProfileForm()
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'title': 'Add New Member',
    }
    return render(request, 'members/member_form.html', context)


@login_required
@user_passes_test(is_admin_or_staff)
def member_edit(request, pk):
    """Edit member information"""
    member = get_object_or_404(Member, pk=pk)
    
    if request.method == 'POST':
        user_form = UserEditForm(request.POST, request.FILES, instance=member.user)
        profile_form = MemberProfileForm(request.POST, instance=member)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            
            messages.success(request, f'Member {member.user.get_full_name()} updated successfully!')
            return redirect('members:member_detail', pk=member.pk)
    else:
        user_form = UserEditForm(instance=member.user)
        profile_form = MemberProfileForm(instance=member)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'member': member,
        'title': 'Edit Member',
    }
    return render(request, 'members/member_form.html', context)


@login_required
@user_passes_test(is_admin_or_staff)
def member_delete(request, pk):
    """Delete a member"""
    member = get_object_or_404(Member, pk=pk)
    
    if request.method == 'POST':
        member_name = member.user.get_full_name()
        user = member.user
        member.delete()
        user.delete()
        
        messages.success(request, f'Member {member_name} deleted successfully!')
        return redirect('members:member_list')
    
    context = {'member': member}
    return render(request, 'members/member_confirm_delete.html', context)
