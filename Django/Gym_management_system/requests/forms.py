from django import forms
from .models import MembershipRequest, TrainerRequest
from memberships.models import MembershipPlan
from trainers.models import Trainer


class MembershipRequestForm(forms.ModelForm):
    """
    Form for submitting membership requests
    """
    
    class Meta:
        model = MembershipRequest
        fields = [
            'first_name', 'last_name', 'email', 'phone_number', 'date_of_birth', 'gender', 'address',
            'emergency_contact_name', 'emergency_contact_phone',
            'blood_group', 'medical_notes', 'height', 'weight', 'fitness_goal',
            'selected_plan'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your first name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your last name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'your.email@example.com'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+91 XXXXXXXXXX'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter your full address'}),
            'emergency_contact_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Emergency contact name'}),
            'emergency_contact_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Emergency contact phone'}),
            'blood_group': forms.Select(attrs={'class': 'form-select'}),
            'medical_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Any medical conditions, allergies, or health concerns'}),
            'height': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Height in cm', 'step': '0.01'}),
            'weight': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Weight in kg', 'step': '0.01'}),
            'fitness_goal': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'What are your fitness goals?'}),
            'selected_plan': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show active membership plans
        self.fields['selected_plan'].queryset = MembershipPlan.objects.filter(is_active=True)


class TrainerRequestForm(forms.ModelForm):
    """
    Form for requesting a personal trainer
    """
    
    class Meta:
        model = TrainerRequest
        fields = [
            'preferred_specialization', 'preferred_trainer', 'sessions_per_week',
            'preferred_time', 'fitness_goals', 'additional_notes'
        ]
        widgets = {
            'preferred_specialization': forms.Select(attrs={'class': 'form-select'}),
            'preferred_trainer': forms.Select(attrs={'class': 'form-select'}),
            'sessions_per_week': forms.Select(attrs={'class': 'form-select'}),
            'preferred_time': forms.Select(attrs={'class': 'form-select'}),
            'fitness_goals': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'What do you want to achieve with personal training?'}),
            'additional_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Any additional information or preferences'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show available trainers
        self.fields['preferred_trainer'].queryset = Trainer.objects.filter(is_available=True)
        self.fields['preferred_trainer'].required = False
