from django import forms
from django.utils import timezone
from .models import Event, EventType
from django.core.exceptions import ValidationError

class EventTypeForm(forms.ModelForm):
    class Meta:
        model = EventType
        fields = ['name', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Marriage, Birthday'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'name': 'Event Name',
            'image': 'Event Image'
        }

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['event_type', 'date', 'venue_location', 'client_name', 'client_phone', 'client_email']
        widgets = {
            'event_type': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={
                'class': 'form-control', 
                'type': 'date',
                'min': timezone.now().date().isoformat()
            }),
            'venue_location': forms.TextInput(attrs={'class': 'form-control'}),
            'client_name': forms.TextInput(attrs={'class': 'form-control'}),
            'client_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'client_email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def clean_date(self):
        date = self.cleaned_data.get('date')
        if date and date < timezone.now().date():
            raise ValidationError("Events cannot be scheduled in the past.")
        return date
