from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Resort, Room, Booking, ResortReview

class ReviewForm(forms.ModelForm):
    class Meta:
        model = ResortReview
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(attrs={'class': 'form-select'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        }

class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email')

class ResortForm(forms.ModelForm):
    class Meta:
        model = Resort
        fields = ['name', 'location', 'description', 'category', 'is_approved', 'is_active', 'owner', 'ar_model']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control px-4 py-3 rounded-4 border-2'}),
            'location': forms.TextInput(attrs={'class': 'form-control px-4 py-3 rounded-4 border-2'}),
            'description': forms.Textarea(attrs={'class': 'form-control px-4 py-3 rounded-4 border-2', 'rows': 4}),
            'category': forms.Select(attrs={'class': 'form-select px-4 py-3 rounded-4 border-2'}),
            'is_approved': forms.CheckboxInput(attrs={'class': 'form-check-input ms-2'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input ms-2'}),
            'owner': forms.Select(attrs={'class': 'form-select px-4 py-3 rounded-4 border-2'}),
            'ar_model': forms.FileInput(attrs={'class': 'form-control px-4 py-3 rounded-4 border-2'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user and user.role != 'admin':
            if 'is_approved' in self.fields:
                del self.fields['is_approved']
            if 'is_active' in self.fields:
                del self.fields['is_active']
            if 'owner' in self.fields:
                del self.fields['owner']

class ResortRegistrationForm(forms.ModelForm):
    class Meta:
        model = Resort
        fields = ['name', 'location', 'description', 'category', 'ar_model'] # Explicitly list fields to exclude is_approved
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control px-4 py-3 rounded-4 border-2'}),
            'location': forms.TextInput(attrs={'class': 'form-control px-4 py-3 rounded-4 border-2'}),
            'description': forms.Textarea(attrs={'class': 'form-control px-4 py-3 rounded-4 border-2', 'rows': 4}),
            'category': forms.Select(attrs={'class': 'form-select px-4 py-3 rounded-4 border-2'}),
            'ar_model': forms.FileInput(attrs={'class': 'form-control px-4 py-3 rounded-4 border-2'}),
        }

class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['room_type', 'capacity', 'price', 'total_rooms', 'available_rooms', 'ar_model']
        widgets = {
            'room_type': forms.Select(attrs={'class': 'form-select px-4 py-3 rounded-4 border-2'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control px-4 py-3 rounded-4 border-2', 'min': '1'}),
            'price': forms.NumberInput(attrs={'class': 'form-control px-4 py-3 rounded-4 border-2', 'placeholder': '₹ per night'}),
            'total_rooms': forms.NumberInput(attrs={'class': 'form-control px-4 py-3 rounded-4 border-2', 'min': '0'}),
            'available_rooms': forms.NumberInput(attrs={'class': 'form-control px-4 py-3 rounded-4 border-2', 'min': '0'}),
            'ar_model': forms.FileInput(attrs={'class': 'form-control px-4 py-3 rounded-4 border-2'}),
        }

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['check_in', 'check_out', 'guests_count']
        widgets = {
            'check_in': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'check_out': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'guests_count': forms.NumberInput(attrs={'min': '1', 'class': 'form-control'}),
        }
