from django import forms
from .models import Booking
from events.models import Event
from vendors.models import Vendor

class BookingForm(forms.ModelForm):
    """
    Form for creating vendor bookings for events.
    """
    class Meta:
        model = Booking
        fields = ['event', 'vendor']
        widgets = {
            'event': forms.Select(attrs={
                'class': 'form-control'
            }),
            'vendor': forms.Select(attrs={
                'class': 'form-control'
            }),
        }
    
    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter events to show only user's events
        if user:
            self.fields['event'].queryset = Event.objects.filter(created_by=user)
