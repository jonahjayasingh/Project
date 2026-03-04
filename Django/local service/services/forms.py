from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
from django.conf import settings
from .models import UserProfile, Review, ServiceProvider
import csv
import os

def is_username_restricted(username):
    """
    Check if a username exists in user_crimes.csv.
    Returns (True, reason) or (False, None)
    """
    if not username:
        return False, None

    csv_path = os.path.join(settings.BASE_DIR, 'user_crimes.csv')

    if not os.path.exists(csv_path):
        return False, None

    try:
        with open(csv_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for row in reader:
                if row.get('username') == username:
                    return True, row.get('crime', 'policy violations')

        return False, None

    except Exception:
        # In production you would log this error
        return False, None

class UserSignupForm(UserCreationForm):
    location = forms.CharField(max_length=200, required=True, help_text="Enter your city or area")

    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ('email',)

    def clean_username(self):
        username = self.cleaned_data.get('username')
        is_restricted, reason = is_username_restricted(username)
        if is_restricted:
            raise ValidationError(
                f"This username is restricted due to {reason}.",
                code='restricted_signup'
            )
        return username

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.location_name = self.cleaned_data['location']
            profile.save()
        return user

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment', 'was_on_time']
        widgets = {
            'rating': forms.Select(choices=[(i, str(i)) for i in range(1, 6)], attrs={'class': 'form-select'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Share your experience...'}),
            'was_on_time': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class ServiceProviderForm(forms.ModelForm):
    class Meta:
        model = ServiceProvider
        fields = ['name', 'categories', 'bio', 'location', 'latitude', 'longitude', 'price_per_hour', 'profile_image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Business/Service Name'}),
            'categories': forms.CheckboxSelectMultiple(),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe your skills and experience...'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City or Area'}),
            'price_per_hour': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Hourly Rate in ₹'}),
            'profile_image': forms.FileInput(attrs={'class': 'form-control'}),
        }

class RestrictedLoginForm(AuthenticationForm):
    """
    Login form that restricts users based on the user_crimes.csv blacklist.
    """
    def clean_username(self):
        username = self.cleaned_data.get('username')
        is_restricted, reason = is_username_restricted(username)
        if is_restricted:
            raise ValidationError(
                "This account has been restricted due to previous system violations.",
                code='restricted'
            )
        return username
