from django import forms
from .models import Prediction

class SkinImageForm(forms.ModelForm):
    class Meta:
        model = Prediction
        fields = ['image']
