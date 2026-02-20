from django import forms
from .models import Room, Bed, Admission

class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['room_number', 'room_type', 'floor', 'cost_per_day', 'description', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})


class BedForm(forms.ModelForm):
    class Meta:
        model = Bed
        fields = ['bed_number', 'room', 'is_active']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})


class AdmissionForm(forms.ModelForm):
    class Meta:
        model = Admission
        fields = [
            'patient', 'bed', 'admission_date', 'discharge_date',
            'reason', 'status', 'discharge_summary', 'discharge_instructions'
        ]
        widgets = {
            'admission_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'discharge_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'reason': forms.Textarea(attrs={'rows': 3}),
            'discharge_summary': forms.Textarea(attrs={'rows': 3}),
            'discharge_instructions': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
        
        # Only show available beds
        self.fields['bed'].queryset = Bed.objects.filter(is_occupied=False, is_active=True).select_related('room')
