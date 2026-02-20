from django import forms
from .models import Payment
from members.models import Member


class PaymentForm(forms.ModelForm):
    """Form for recording payments"""
    
    class Meta:
        model = Payment
        fields = ['member', 'amount', 'payment_method', 'payment_type', 'status',
                  'transaction_id', 'payment_date', 'description']
        widgets = {
            'payment_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
        
        # Filter to show only active members
        self.fields['member'].queryset = Member.objects.filter(status='active')
        
        # Set current user as received_by in view
        self.fields['transaction_id'].required = False
        self.fields['description'].required = False
