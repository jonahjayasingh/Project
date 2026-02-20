from django import forms
from .models import Appointment
from patients.models import Patient
from doctors.models import Doctor

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['patient', 'doctor', 'appointment_date', 'appointment_time', 'duration_minutes', 'reason', 'notes', 'status']
        widgets = {
            'appointment_date': forms.DateInput(attrs={'type': 'date'}),
            'appointment_time': forms.TimeInput(attrs={'type': 'time'}),
            'reason': forms.Textarea(attrs={'rows': 3}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
        
        # Only show active patients and doctors
        self.fields['patient'].queryset = Patient.objects.filter(status='active').select_related('user')
        self.fields['doctor'].queryset = Doctor.objects.filter(status='active').select_related('user', 'department')
