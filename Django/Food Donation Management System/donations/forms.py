from django import forms
from .models import Donation
from accounts.models import CustomUser

class DonationForm(forms.ModelForm):
    class Meta:
        model = Donation
        fields = ['food_type', 'quantity', 'cooked_time', 'pickup_time', 'address', 'latitude', 'longitude']
        widgets = {
            'pickup_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'cooked_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'food_type': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Rice, Vegetables, Cooked Meals'}),
            'quantity': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 5 kg, 10 servings'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter full pickup address'}),
            'latitude': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.000001', 'placeholder': 'e.g., 28.6139'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.000001', 'placeholder': 'e.g., 77.2090'}),
        }
        labels = {
            'food_type': 'Food Type',
            'quantity': 'Quantity',
            'cooked_time': 'Cooked Time (Optional)',
            'pickup_time': 'Pickup Time',
            'address': 'Pickup Address',
            'latitude': 'Latitude (Optional)',
            'longitude': 'Longitude (Optional)',
        }

class AssignVolunteerForm(forms.Form):
    volunteer = forms.ModelChoiceField(
        queryset=CustomUser.objects.filter(role='volunteer', is_approved=True),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Select Volunteer'
    )

