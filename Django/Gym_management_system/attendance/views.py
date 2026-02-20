from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.utils import timezone
from .models import Attendance
from .forms import CheckInForm


def is_admin_or_staff(user):
    """Check if user is admin or staff"""
    return user.is_authenticated and (user.is_admin() or user.is_staff_member())


@login_required
@user_passes_test(is_admin_or_staff)
def attendance_list(request):
    """List all attendance records"""
    attendance_records = Attendance.objects.select_related('member__user').all()
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        attendance_records = attendance_records.filter(
            Q(member__user__first_name__icontains=search_query) |
            Q(member__user__last_name__icontains=search_query)
        )
    
    # Filter by date
    date_filter = request.GET.get('date', '')
    if date_filter:
        attendance_records = attendance_records.filter(date=date_filter)
    
    # Filter by type
    type_filter = request.GET.get('type', '')
    if type_filter:
        attendance_records = attendance_records.filter(attendance_type=type_filter)
    
    # Pagination
    paginator = Paginator(attendance_records, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'date_filter': date_filter,
        'type_filter': type_filter,
        'type_choices': Attendance.TYPE_CHOICES,
    }
    return render(request, 'attendance/attendance_list.html', context)


@login_required
@user_passes_test(is_admin_or_staff)
def check_in(request):
    """Check in a member"""
    if request.method == 'POST':
        form = CheckInForm(request.POST)
        
        if form.is_valid():
            attendance = form.save()
            messages.success(request, f'{attendance.member.user.get_full_name()} checked in successfully!')
            return redirect('attendance:attendance_list')
    else:
        form = CheckInForm()
    
    context = {
        'form': form,
        'title': 'Member Check-In',
    }
    return render(request, 'attendance/check_in_form.html', context)


@login_required
@user_passes_test(is_admin_or_staff)
def check_out(request, pk):
    """Check out a member"""
    attendance = get_object_or_404(Attendance, pk=pk)
    
    if attendance.check_out_time:
        messages.warning(request, 'Member already checked out!')
        return redirect('attendance:attendance_list')
    
    if request.method == 'POST':
        attendance.check_out_time = timezone.now()
        attendance.save()
        messages.success(request, f'{attendance.member.user.get_full_name()} checked out successfully!')
        return redirect('attendance:attendance_list')
    
    context = {'attendance': attendance}
    return render(request, 'attendance/check_out_confirm.html', context)


@login_required
@user_passes_test(is_admin_or_staff)
def attendance_detail(request, pk):
    """View attendance details"""
    attendance = get_object_or_404(Attendance.objects.select_related('member__user'), pk=pk)
    
    context = {'attendance': attendance}
    return render(request, 'attendance/attendance_detail.html', context)
