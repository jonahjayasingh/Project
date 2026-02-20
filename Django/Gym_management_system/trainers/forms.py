from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Trainer, TrainerAvailability, TrainerMemberAssignment
from accounts.models import CustomUser
from members.models import Member


class TrainerRegistrationForm(UserCreationForm):
    """Form for registering new trainers"""
    
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)
    phone_number = forms.CharField(max_length=15, required=True)
    date_of_birth = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    gender = forms.ChoiceField(
        choices=[('', 'Select Gender')] + list(CustomUser.GENDER_CHOICES),
        required=False
    )
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)
    
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2', 'first_name', 'last_name', 
                  'phone_number', 'date_of_birth', 'gender', 'address', 'profile_photo']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            if field_name == 'profile_photo':
                field.widget.attrs['class'] = 'form-control-file'
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'trainer'
        if commit:
            user.save()
        return user


class TrainerUserEditForm(forms.ModelForm):
    """Form for editing trainer user information"""
    
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'phone_number', 
                  'date_of_birth', 'gender', 'address', 'profile_photo']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            if field_name == 'profile_photo':
                field.widget.attrs['class'] = 'form-control-file'


class TrainerProfileForm(forms.ModelForm):
    """Form for trainer profile information"""
    
    class Meta:
        model = Trainer
        fields = ['specialization', 'certifications', 'experience_years', 
                  'hourly_rate', 'bio', 'is_available']
        widgets = {
            'certifications': forms.Textarea(attrs={'rows': 3, 'placeholder': 'List certifications (one per line)'}),
            'bio': forms.Textarea(attrs={'rows': 4}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name == 'is_available':
                field.widget.attrs['class'] = 'form-check-input'
            else:
                field.widget.attrs['class'] = 'form-control'


class TrainerAvailabilityForm(forms.ModelForm):
    """Form for trainer availability schedule"""
    
    class Meta:
        model = TrainerAvailability
        fields = ['day_of_week', 'start_time', 'end_time', 'is_active']
        widgets = {
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name == 'is_active':
                field.widget.attrs['class'] = 'form-check-input'
            else:
                field.widget.attrs['class'] = 'form-control'


class TrainerAssignmentForm(forms.ModelForm):
    """Form for assigning trainers to members"""
    
    class Meta:
        model = TrainerMemberAssignment
        fields = ['trainer', 'member', 'start_date', 'end_date', 'status', 
                  'sessions_per_week', 'notes']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
        
        # Filter to show only active trainers and members
        self.fields['trainer'].queryset = Trainer.objects.filter(is_available=True)
        self.fields['member'].queryset = Member.objects.filter(status='active')
