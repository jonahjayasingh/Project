from django import forms
from .models import Vendor

class VendorForm(forms.ModelForm):
    """
    Form for creating and editing vendors (Admin only).
    """
    class Meta:
        model = Vendor
        fields = ['name', 'category', 'price']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Vendor Name'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Service Price'
            }),
        }
