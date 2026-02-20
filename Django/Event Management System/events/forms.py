from django import forms
from .models import Event

class EventForm(forms.ModelForm):
    """
    Form for creating and editing events.
    """
    class Meta:
        model = Event
        fields = ['name', 'date', 'venue', 'expected_guests', 'budget']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Event Name'
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'venue': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Event Venue'
            }),
            'expected_guests': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Expected Number of Guests'
            }),
            'budget': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Total Budget'
            }),
        }
