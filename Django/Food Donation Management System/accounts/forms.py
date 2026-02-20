from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter out 'admin' from role choices
        if 'role' in self.fields:
            choices = list(self.fields['role'].choices)
            self.fields['role'].choices = [c for c in choices if c[0] != 'admin']

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = UserCreationForm.Meta.fields + ('role', 'phone_number', 'email')
