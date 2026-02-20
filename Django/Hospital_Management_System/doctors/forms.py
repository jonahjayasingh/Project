from django import forms
from .models import Department, Doctor
from accounts.models import User

class DoctorUserForm(forms.ModelForm):
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


class DoctorProfileForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = [
            'department', 'specialization', 'qualifications', 'experience_years',
            'license_number', 'consultation_fee', 'available_days',
            'available_time_start', 'available_time_end', 'status'
        ]
        widgets = {
            'qualifications': forms.Textarea(attrs={'rows': 3}),
            'available_time_start': forms.TimeInput(attrs={'type': 'time'}),
            'available_time_end': forms.TimeInput(attrs={'type': 'time'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})


class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'description', 'head_of_department', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
        
        # Only show doctors for head_of_department
        self.fields['head_of_department'].queryset = User.objects.filter(role='doctor')
