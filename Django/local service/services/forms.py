from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile, Review, ServiceProvider

class UserSignupForm(UserCreationForm):
    location = forms.CharField(max_length=200, required=True, help_text="Enter your city or area")

    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ('email',)

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
