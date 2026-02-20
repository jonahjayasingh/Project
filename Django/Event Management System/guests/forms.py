from django import forms
from .models import Guest
from events.models import Event

class GuestForm(forms.ModelForm):
    """
    Form for adding guests to events.
    """
    class Meta:
        model = Guest
        fields = ['event', 'name', 'contact', 'category']
        widgets = {
            'event': forms.Select(attrs={
                'class': 'form-control'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Guest Name'
            }),
            'contact': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Contact (Phone/Email)'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
        }
    
    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter events to show only user's events
        if user:
            self.fields['event'].queryset = Event.objects.filter(created_by=user)
