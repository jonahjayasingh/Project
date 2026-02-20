from django import forms
from .models import Patient, PatientDocument
from accounts.models import User

class PatientUserForm(forms.ModelForm):
    """Form for creating/updating patient user account"""
    password = forms.CharField(widget=forms.PasswordInput(), required=False)
    confirm_password = forms.CharField(widget=forms.PasswordInput(), required=False)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'phone', 'address', 'date_of_birth']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match")
        
        return cleaned_data


class PatientProfileForm(forms.ModelForm):
    """Form for patient medical profile"""
    class Meta:
        model = Patient
        fields = [
            'blood_group', 'height', 'weight',
            'emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relation',
            'allergies', 'chronic_conditions', 'current_medications', 'past_surgeries',
            'status', 'admission_date', 'discharge_date'
        ]
        widgets = {
            'admission_date': forms.DateInput(attrs={'type': 'date'}),
            'discharge_date': forms.DateInput(attrs={'type': 'date'}),
            'allergies': forms.Textarea(attrs={'rows': 2}),
            'chronic_conditions': forms.Textarea(attrs={'rows': 2}),
            'current_medications': forms.Textarea(attrs={'rows': 2}),
            'past_surgeries': forms.Textarea(attrs={'rows': 2}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})


class PatientDocumentForm(forms.ModelForm):
    """Form for uploading patient documents"""
    class Meta:
        model = PatientDocument
        fields = ['document_type', 'title', 'file', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
