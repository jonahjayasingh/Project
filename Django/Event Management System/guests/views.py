from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from accounts.decorators import client_required
from .models import Guest
from .forms import GuestForm

@client_required
def guest_list_view(request):
    """
    List all guests for the current client's events.
    """
    guests = Guest.objects.filter(event__created_by=request.user)
    return render(request, 'guests/guest_list.html', {'guests': guests})


@client_required
def guest_create_view(request):
    """
    Add a new guest to an event.
    """
    if request.method == 'POST':
        form = GuestForm(user=request.user, data=request.POST)
        if form.is_valid():
            guest = form.save()
            messages.success(
                request,
                f'Guest "{guest.name}" added to "{guest.event.name}" successfully!'
            )
            return redirect('guests:guest_list')
    else:
        form = GuestForm(user=request.user)
    
    return render(request, 'guests/guest_form.html', {'form': form})


@client_required
def guest_delete_view(request, pk):
    """
    Delete a guest.
    """
    guest = get_object_or_404(Guest, pk=pk, event__created_by=request.user)
    
    if request.method == 'POST':
        guest_name = guest.name
        event_name = guest.event.name
        guest.delete()
        messages.success(
            request,
            f'Guest "{guest_name}" removed from "{event_name}"!'
        )
        return redirect('guests:guest_list')
    
    return render(request, 'guests/guest_confirm_delete.html', {'guest': guest})
