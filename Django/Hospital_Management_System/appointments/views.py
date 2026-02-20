from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.utils import timezone
from .models import Appointment
from .forms import AppointmentForm

@login_required
def appointment_list(request):
    """List all appointments with filters"""
    appointments = Appointment.objects.select_related('patient__user', 'doctor__user').all()
    
    # Search
    search_query = request.GET.get('search', '')
    if search_query:
        appointments = appointments.filter(
            Q(appointment_id__icontains=search_query) |
            Q(patient__user__first_name__icontains=search_query) |
            Q(patient__user__last_name__icontains=search_query) |
            Q(doctor__user__first_name__icontains=search_query) |
            Q(doctor__user__last_name__icontains=search_query)
        )
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        appointments = appointments.filter(status=status_filter)
    
    # Filter by date
    date_filter = request.GET.get('date', '')
    if date_filter:
        appointments = appointments.filter(appointment_date=date_filter)
    
    # Order by date and time
    appointments = appointments.order_by('-appointment_date', '-appointment_time')
    
    # Pagination
    paginator = Paginator(appointments, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'date_filter': date_filter,
    }
    return render(request, 'appointments/appointment_list.html', context)


@login_required
def appointment_detail(request, pk):
    """View appointment details"""
    appointment = get_object_or_404(
        Appointment.objects.select_related('patient__user', 'doctor__user', 'booked_by'),
        pk=pk
    )
    
    context = {'appointment': appointment}
    return render(request, 'appointments/appointment_detail.html', context)


@login_required
def appointment_create(request):
    """Create new appointment"""
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.booked_by = request.user
            try:
                appointment.full_clean()  # Validate overlap
                appointment.save()
                messages.success(request, f'Appointment {appointment.appointment_id} created successfully!')
                return redirect('appointments:appointment_detail', pk=appointment.pk)
            except Exception as e:
                messages.error(request, f'Error: {str(e)}')
    else:
        form = AppointmentForm()
    
    context = {
        'form': form,
        'action': 'Create'
    }
    return render(request, 'appointments/appointment_form.html', context)


@login_required
def appointment_update(request, pk):
    """Update appointment"""
    appointment = get_object_or_404(Appointment, pk=pk)
    
    if request.method == 'POST':
        form = AppointmentForm(request.POST, instance=appointment)
        if form.is_valid():
            try:
                appointment = form.save(commit=False)
                appointment.full_clean()  # Validate overlap
                appointment.save()
                messages.success(request, f'Appointment {appointment.appointment_id} updated successfully!')
                return redirect('appointments:appointment_detail', pk=appointment.pk)
            except Exception as e:
                messages.error(request, f'Error: {str(e)}')
    else:
        form = AppointmentForm(instance=appointment)
    
    context = {
        'form': form,
        'appointment': appointment,
        'action': 'Update'
    }
    return render(request, 'appointments/appointment_form.html', context)


@login_required
def appointment_delete(request, pk):
    """Delete appointment"""
    appointment = get_object_or_404(Appointment, pk=pk)
    
    if request.method == 'POST':
        appointment_id = appointment.appointment_id
        appointment.delete()
        messages.success(request, f'Appointment {appointment_id} deleted successfully!')
        return redirect('appointments:appointment_list')
    
    context = {'appointment': appointment}
    return render(request, 'appointments/appointment_confirm_delete.html', context)


@login_required
def appointment_cancel(request, pk):
    """Cancel appointment"""
    appointment = get_object_or_404(Appointment, pk=pk)
    
    if request.method == 'POST':
        cancellation_reason = request.POST.get('cancellation_reason', '')
        appointment.status = 'cancelled'
        appointment.cancellation_reason = cancellation_reason
        appointment.cancelled_at = timezone.now()
        appointment.save()
        messages.success(request, f'Appointment {appointment.appointment_id} cancelled successfully!')
        return redirect('appointments:appointment_detail', pk=appointment.pk)
    
    context = {'appointment': appointment}
    return render(request, 'appointments/appointment_cancel.html', context)
