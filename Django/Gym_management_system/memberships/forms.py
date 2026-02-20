from django import forms
from .models import MembershipPlan, MemberMembership
from members.models import Member


class MembershipPlanForm(forms.ModelForm):
    """Form for creating/editing membership plans"""
    
    class Meta:
        model = MembershipPlan
        fields = ['name', 'description', 'duration_months', 'price', 'access_level', 
                  'benefits', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'benefits': forms.Textarea(attrs={'rows': 4, 'placeholder': 'List benefits (one per line)'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name == 'is_active':
                field.widget.attrs['class'] = 'form-check-input'
            else:
                field.widget.attrs['class'] = 'form-control'


class MemberMembershipForm(forms.ModelForm):
    """Form for assigning plans to members"""
    
    class Meta:
        model = MemberMembership
        fields = ['member', 'plan', 'start_date', 'end_date', 'status', 
                  'payment_status', 'amount_paid', 'notes']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
        
        # Filter to show only active members and plans
        self.fields['member'].queryset = Member.objects.filter(status='active')
        self.fields['plan'].queryset = MembershipPlan.objects.filter(is_active=True)
        self.fields['end_date'].required = False


class FreezeForm(forms.Form):
    """Form for freezing memberships"""
    
    freeze_days = forms.IntegerField(
        min_value=1,
        max_value=90,
        label='Freeze Duration (days)',
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
