from django import forms
from .models import FitnessClass, ClassSchedule, ClassBooking
from trainers.models import Trainer
from members.models import Member


class FitnessClassForm(forms.ModelForm):
    """Form for fitness class details"""
    
    class Meta:
        model = FitnessClass
        fields = ['name', 'description', 'difficulty_level', 'duration_minutes', 
                  'capacity', 'image', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name == 'is_active':
                field.widget.attrs['class'] = 'form-check-input'
            elif field_name == 'image':
                field.widget.attrs['class'] = 'form-control-file'
            else:
                field.widget.attrs['class'] = 'form-control'


class ClassScheduleForm(forms.ModelForm):
    """Form for scheduling classes"""
    
    class Meta:
        model = ClassSchedule
        fields = ['fitness_class', 'trainer', 'day_of_week', 'start_time', 
                  'room_location', 'is_active']
        widgets = {
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name == 'is_active':
                field.widget.attrs['class'] = 'form-check-input'
            else:
                field.widget.attrs['class'] = 'form-control'
        
        # Filter to show only available trainers
        self.fields['trainer'].queryset = Trainer.objects.filter(is_available=True)
        self.fields['fitness_class'].queryset = FitnessClass.objects.filter(is_active=True)


class ClassBookingForm(forms.ModelForm):
    """Form for booking members into classes"""
    
    class Meta:
        model = ClassBooking
        fields = ['schedule', 'member', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
        
        # Filter to show only active schedules and members
        self.fields['schedule'].queryset = ClassSchedule.objects.filter(is_active=True).select_related('fitness_class', 'trainer__user')
        self.fields['member'].queryset = Member.objects.filter(status='active')
