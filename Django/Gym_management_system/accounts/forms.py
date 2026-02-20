from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser


class MemberRegistrationForm(UserCreationForm):
    """Form for registering new members"""
    
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)
    phone_number = forms.CharField(max_length=15, required=True)
    date_of_birth = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    gender = forms.ChoiceField(
        choices=[('', 'Select Gender')] + list(CustomUser.GENDER_CHOICES),
        required=False
    )
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)
    
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2', 'first_name', 'last_name', 
                  'phone_number', 'date_of_birth', 'gender', 'address', 'profile_photo']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to all fields
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            if field_name == 'profile_photo':
                field.widget.attrs['class'] = 'form-control-file'
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'member'  # Set role to member
        if commit:
            user.save()
        return user


class UserEditForm(forms.ModelForm):
    """Form for editing user information"""
    
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'phone_number', 
                  'date_of_birth', 'gender', 'address', 'profile_photo']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            if field_name == 'profile_photo':
                field.widget.attrs['class'] = 'form-control-file'
