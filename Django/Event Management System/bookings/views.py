from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import IntegrityError
from accounts.decorators import client_required
from .models import Booking
from .forms import BookingForm
from vendors.models import Vendor

@client_required
def booking_list_view(request):
    """
    List all bookings for the current client's events.
    """
    bookings = Booking.objects.filter(event__created_by=request.user)
    return render(request, 'bookings/booking_list.html', {'bookings': bookings})


@client_required
def booking_create_view(request):
    """
    Create a new vendor booking.
    Prevents duplicate bookings for same vendor on same event.
    """
    if request.method == 'POST':
        form = BookingForm(user=request.user, data=request.POST)
        if form.is_valid():
            try:
                booking = form.save(commit=False)
                # Price is auto-populated in the model's save method
                booking.save()
                messages.success(
                    request,
                    f'Vendor "{booking.vendor.name}" booked successfully for "{booking.event.name}"!'
                )
                return redirect('bookings:booking_list')
            except IntegrityError:
                messages.error(
                    request,
                    'This vendor is already booked for this event!'
                )
    else:
        form = BookingForm(user=request.user)
    
    # Get all vendors for display
    vendors = Vendor.objects.all()
    
    return render(request, 'bookings/booking_form.html', {
        'form': form,
        'vendors': vendors
    })


@client_required
def booking_delete_view(request, pk):
    """
    Delete a booking.
    """
    booking = get_object_or_404(Booking, pk=pk, event__created_by=request.user)
    
    if request.method == 'POST':
        vendor_name = booking.vendor.name
        event_name = booking.event.name
        booking.delete()
        messages.success(
            request,
            f'Booking for "{vendor_name}" removed from "{event_name}"!'
        )
        return redirect('bookings:booking_list')
    
    return render(request, 'bookings/booking_confirm_delete.html', {'booking': booking})
