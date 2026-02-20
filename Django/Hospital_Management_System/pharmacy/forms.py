from django import forms
from .models import Medicine, Prescription, PrescriptionItem

class MedicineForm(forms.ModelForm):
    class Meta:
        model = Medicine
        fields = [
            'name', 'generic_name', 'category', 'manufacturer', 'description',
            'stock_quantity', 'unit_price', 'reorder_level',
            'expiry_date', 'batch_number', 'is_active'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'expiry_date': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})


class PrescriptionForm(forms.ModelForm):
    class Meta:
        model = Prescription
        fields = ['medical_record', 'patient', 'doctor', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})


class PrescriptionItemForm(forms.ModelForm):
    class Meta:
        model = PrescriptionItem
        fields = ['medicine', 'dosage', 'frequency', 'duration_days', 'quantity', 'instructions']
        widgets = {
            'instructions': forms.Textarea(attrs={'rows': 2}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
