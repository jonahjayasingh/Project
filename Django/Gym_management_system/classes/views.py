from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q, Count
from django.core.paginator import Paginator
from .models import FitnessClass, ClassSchedule, ClassBooking
from .forms import FitnessClassForm, ClassScheduleForm, ClassBookingForm


def is_admin_or_staff(user):
    """Check if user is admin or staff"""
    return user.is_authenticated and (user.is_admin() or user.is_staff_member())


@login_required
@user_passes_test(is_admin_or_staff)
def class_list(request):
    """List all fitness classes"""
    classes = FitnessClass.objects.all()
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        classes = classes.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Filter by difficulty
    difficulty_filter = request.GET.get('difficulty', '')
    if difficulty_filter:
        classes = classes.filter(difficulty_level=difficulty_filter)
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        classes = classes.filter(is_active=(status_filter == 'true'))
    
    # Annotate with schedule count
    classes = classes.annotate(schedule_count=Count('schedules', filter=Q(schedules__is_active=True)))
    
    # Pagination
    paginator = Paginator(classes, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'difficulty_filter': difficulty_filter,
        'status_filter': status_filter,
        'difficulty_choices': FitnessClass.DIFFICULTY_CHOICES,
    }
    return render(request, 'classes/class_list.html', context)


@login_required
@user_passes_test(is_admin_or_staff)
def class_detail(request, pk):
    """View class details"""
    fitness_class = get_object_or_404(FitnessClass, pk=pk)
    
    # Get class schedules
    schedules = fitness_class.schedules.filter(is_active=True).select_related('trainer__user').order_by('day_of_week', 'start_time')
    
    # Get recent bookings
    recent_bookings = ClassBooking.objects.filter(
        schedule__fitness_class=fitness_class
    ).select_related('member__user', 'schedule').order_by('-booking_date')[:20]
    
    context = {
        'fitness_class': fitness_class,
        'schedules': schedules,
        'recent_bookings': recent_bookings,
    }
    return render(request, 'classes/class_detail.html', context)


@login_required
@user_passes_test(is_admin_or_staff)
def class_create(request):
    """Create a new fitness class"""
    if request.method == 'POST':
        form = FitnessClassForm(request.POST, request.FILES)
        
        if form.is_valid():
            fitness_class = form.save()
            messages.success(request, f'Class "{fitness_class.name}" created successfully!')
            return redirect('classes:class_detail', pk=fitness_class.pk)
    else:
        form = FitnessClassForm()
    
    context = {
        'form': form,
        'title': 'Add New Class',
    }
    return render(request, 'classes/class_form.html', context)


@login_required
@user_passes_test(is_admin_or_staff)
def class_edit(request, pk):
    """Edit fitness class"""
    fitness_class = get_object_or_404(FitnessClass, pk=pk)
    
    if request.method == 'POST':
        form = FitnessClassForm(request.POST, request.FILES, instance=fitness_class)
        
        if form.is_valid():
            form.save()
            messages.success(request, f'Class "{fitness_class.name}" updated successfully!')
            return redirect('classes:class_detail', pk=fitness_class.pk)
    else:
        form = FitnessClassForm(instance=fitness_class)
    
    context = {
        'form': form,
        'fitness_class': fitness_class,
        'title': 'Edit Class',
    }
    return render(request, 'classes/class_form.html', context)


@login_required
@user_passes_test(is_admin_or_staff)
def class_delete(request, pk):
    """Delete a fitness class"""
    fitness_class = get_object_or_404(FitnessClass, pk=pk)
    
    if request.method == 'POST':
        class_name = fitness_class.name
        fitness_class.delete()
        messages.success(request, f'Class "{class_name}" deleted successfully!')
        return redirect('classes:class_list')
    
    context = {'fitness_class': fitness_class}
    return render(request, 'classes/class_confirm_delete.html', context)


@login_required
@user_passes_test(is_admin_or_staff)
def schedule_create(request, class_pk):
    """Add schedule for a class"""
    fitness_class = get_object_or_404(FitnessClass, pk=class_pk)
    
    if request.method == 'POST':
        form = ClassScheduleForm(request.POST)
        
        if form.is_valid():
            schedule = form.save()
            messages.success(request, 'Schedule added successfully!')
            return redirect('classes:class_detail', pk=fitness_class.pk)
    else:
        form = ClassScheduleForm(initial={'fitness_class': fitness_class})
    
    context = {
        'form': form,
        'fitness_class': fitness_class,
        'title': 'Add Schedule',
    }
    return render(request, 'classes/schedule_form.html', context)


@login_required
@user_passes_test(is_admin_or_staff)
def schedule_edit(request, pk):
    """Edit class schedule"""
    schedule = get_object_or_404(ClassSchedule, pk=pk)
    
    if request.method == 'POST':
        form = ClassScheduleForm(request.POST, instance=schedule)
        
        if form.is_valid():
            form.save()
            messages.success(request, 'Schedule updated successfully!')
            return redirect('classes:class_detail', pk=schedule.fitness_class.pk)
    else:
        form = ClassScheduleForm(instance=schedule)
    
    context = {
        'form': form,
        'schedule': schedule,
        'fitness_class': schedule.fitness_class,  # Added this line
        'title': 'Edit Schedule',
    }
    return render(request, 'classes/schedule_form.html', context)


@login_required
@user_passes_test(is_admin_or_staff)
def schedule_delete(request, pk):
    """Delete class schedule"""
    schedule = get_object_or_404(ClassSchedule, pk=pk)
    fitness_class = schedule.fitness_class
    
    if request.method == 'POST':
        schedule.delete()
        messages.success(request, 'Schedule deleted successfully!')
        return redirect('classes:class_detail', pk=fitness_class.pk)
    
    context = {
        'schedule': schedule,
        'fitness_class': fitness_class,
    }
    return render(request, 'classes/schedule_confirm_delete.html', context)


@login_required
@user_passes_test(is_admin_or_staff)
def booking_list(request):
    """List all class bookings"""
    bookings = ClassBooking.objects.select_related('member__user', 'schedule__fitness_class', 'schedule__trainer__user').all()
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        bookings = bookings.filter(status=status_filter)
    
    # Pagination
    paginator = Paginator(bookings, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'bookings': page_obj,
        'status_filter': status_filter,
        'status_choices': ClassBooking.STATUS_CHOICES,
    }
    return render(request, 'classes/booking_list.html', context)


@login_required
@user_passes_test(is_admin_or_staff)
def booking_create(request):
    """Create class booking"""
    if request.method == 'POST':
        form = ClassBookingForm(request.POST)
        
        if form.is_valid():
            booking = form.save()
            messages.success(request, f'Booking created for {booking.member.user.get_full_name()}!')
            return redirect('classes:booking_list')
    else:
        schedule_pk = request.GET.get('schedule')
        initial = {}
        if schedule_pk:
            initial['schedule'] = get_object_or_404(ClassSchedule, pk=schedule_pk)
        form = ClassBookingForm(initial=initial)
    
    context = {
        'form': form,
        'title': 'Create Booking',
    }
    return render(request, 'classes/booking_form.html', context)


@login_required
@user_passes_test(is_admin_or_staff)
def booking_cancel(request, pk):
    """Cancel a booking"""
    booking = get_object_or_404(ClassBooking, pk=pk)
    
    if request.method == 'POST':
        booking.cancel_booking()
        messages.success(request, 'Booking cancelled successfully!')
        return redirect('classes:booking_list')
    
    context = {'booking': booking}
    return render(request, 'classes/booking_confirm_cancel.html', context)
