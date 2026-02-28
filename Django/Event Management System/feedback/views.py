from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Feedback
from .forms import FeedbackForm
from events.models import Event
from accounts.decorators import admin_required

@login_required
def submit_feedback_view(request, event_id):
    event = get_object_or_404(Event, id=event_id, client=request.user)
    
    # Check if feedback already exists
    if hasattr(event, 'feedback'):
        messages.info(request, "You have already submitted feedback for this event.")
        return redirect('events:event_detail', pk=event.pk)

    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.event = event
            feedback.save()
            messages.success(request, "Thank you for your valuable feedback!")
            return redirect('events:event_detail', pk=event.pk)
    else:
        form = FeedbackForm()
    
    return render(request, 'feedback/feedback_form.html', {'form': form, 'event': event})

@admin_required
def admin_feedback_list_view(request):
    feedbacks = Feedback.objects.all().order_by('-created_at')
    return render(request, 'feedback/admin_feedback_list.html', {'feedbacks': feedbacks})
