from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from accounts.decorators import admin_required, client_required
from .models import Event, EventType
from .forms import EventForm, EventTypeForm

@client_required
def event_list_view(request):
    events = Event.objects.filter(client=request.user)
    return render(request, 'events/event_list.html', {'events': events})

@client_required
def event_detail_view(request, pk):
    event = get_object_or_404(Event, pk=pk, client=request.user)
    return render(request, 'events/event_detail.html', {'event': event})

@client_required
def event_create_view(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.client = request.user
            event.save()
            messages.success(request, 'Event created successfully!')
            return redirect('events:event_detail', pk=event.pk)
    else:
        # Pre-fill with user details
        form = EventForm(initial={
            'client_name': f"{request.user.first_name} {request.user.last_name}",
            'client_email': request.user.email
        })
    return render(request, 'events/event_form.html', {'form': form, 'title': 'Create Event'})

@client_required
def event_update_view(request, pk):
    event = get_object_or_404(Event, pk=pk, client=request.user)
    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, 'Event updated successfully!')
            return redirect('events:event_detail', pk=event.pk)
    else:
        form = EventForm(instance=event)
    return render(request, 'events/event_form.html', {'form': form, 'title': 'Update Event'})

@client_required
def event_delete_view(request, pk):
    event = get_object_or_404(Event, pk=pk, client=request.user)
    if request.method == 'POST':
        event.delete()
        messages.success(request, 'Event deleted successfully!')
        return redirect('events:event_list')
    return render(request, 'events/event_confirm_delete.html', {'event': event})

# Admin Views
@admin_required
def admin_event_types_view(request):
    types = EventType.objects.all()
    if request.method == 'POST':
        form = EventTypeForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Event type added.')
            return redirect('events:admin_event_types')
    else:
        form = EventTypeForm()
    return render(request, 'events/admin_event_types.html', {'types': types, 'form': form})

@admin_required
def admin_all_events_view(request):
    events = Event.objects.all().order_by('-date')
    return render(request, 'events/admin_all_events.html', {'events': events})

@admin_required
def admin_event_type_delete(request, pk):
    etype = get_object_or_404(EventType, pk=pk)
    if request.method == 'POST':
        etype.delete()
        messages.success(request, 'Event type removed.')
        return redirect('events:admin_event_types')
    return render(request, 'confirm_delete.html', {'object': etype})

@admin_required
def admin_event_type_update(request, pk):
    etype = get_object_or_404(EventType, pk=pk)
    if request.method == 'POST':
        form = EventTypeForm(request.POST, request.FILES, instance=etype)
        if form.is_valid():
            form.save()
            messages.success(request, 'Event type updated.')
            return redirect('events:admin_event_types')
    else:
        form = EventTypeForm(instance=etype)
    return render(request, 'events/admin_event_type_form.html', {'form': form, 'etype': etype})
