from django import forms
from .models import Member
from accounts.models import CustomUser


class MemberProfileForm(forms.ModelForm):
    """Form for member profile information"""
    
    class Meta:
        model = Member
        fields = ['emergency_contact_name', 'emergency_contact_phone', 'blood_group', 
                  'medical_notes', 'height', 'weight', 'fitness_goal']
        widgets = {
            'medical_notes': forms.Textarea(attrs={'rows': 3}),
            'fitness_goal': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
