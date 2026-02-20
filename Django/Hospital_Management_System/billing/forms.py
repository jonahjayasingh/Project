from django import forms
from .models import Bill, Payment

class BillForm(forms.ModelForm):
    class Meta:
        model = Bill
        fields = [
            'patient', 'appointment', 'consultation_fee', 'medicine_charges',
            'room_charges', 'lab_charges', 'other_charges', 'discount', 'tax',
            'payment_status', 'payment_method', 'notes'
        ]
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['amount', 'payment_method', 'transaction_id', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
