from django import forms
from .models import Attendance
from members.models import Member


class CheckInForm(forms.ModelForm):
    """Form for member check-in"""
    
    class Meta:
        model = Attendance
        fields = ['member', 'attendance_type', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 2}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
        
        # Filter to show only active members
        self.fields['member'].queryset = Member.objects.filter(status='active')
        self.fields['notes'].required = False
