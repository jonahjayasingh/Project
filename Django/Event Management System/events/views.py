from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from accounts.decorators import client_required
from .models import Event
from .forms import EventForm

@client_required
def event_list_view(request):
    """
    List all events created by the current client.
    """
    events = Event.objects.filter(created_by=request.user)
    return render(request, 'events/event_list.html', {'events': events})


@client_required
def event_detail_view(request, pk):
    """
    View event details including budget tracker.
    """
    event = get_object_or_404(Event, pk=pk, created_by=request.user)
    
    # Budget calculations
    total_bookings = event.total_bookings_cost()
    remaining_budget = event.remaining_budget()
    
    context = {
        'event': event,
        'total_bookings': total_bookings,
        'remaining_budget': remaining_budget,
        'bookings': event.bookings.all(),
        'guests': event.guests.all(),
    }
    return render(request, 'events/event_detail.html', context)


@client_required
def event_create_view(request):
    """
    Create a new event.
    """
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user
            event.save()
            messages.success(request, f'Event "{event.name}" created successfully!')
            return redirect('events:event_detail', pk=event.pk)
    else:
        form = EventForm()
    
    return render(request, 'events/event_form.html', {'form': form, 'action': 'Create'})


@client_required
def event_update_view(request, pk):
    """
    Update an existing event.
    """
    event = get_object_or_404(Event, pk=pk, created_by=request.user)
    
    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, f'Event "{event.name}" updated successfully!')
            return redirect('events:event_detail', pk=event.pk)
    else:
        form = EventForm(instance=event)
    
    return render(request, 'events/event_form.html', {
        'form': form,
        'action': 'Update',
        'event': event
    })


@client_required
def event_delete_view(request, pk):
    """
    Delete an event.
    """
    event = get_object_or_404(Event, pk=pk, created_by=request.user)
    
    if request.method == 'POST':
        event_name = event.name
        event.delete()
        messages.success(request, f'Event "{event_name}" deleted successfully!')
        return redirect('events:event_list')
    
    return render(request, 'events/event_confirm_delete.html', {'event': event})
