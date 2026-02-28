from django import forms
from .models import Service, ServicePortfolio

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'description', 'base_price', 'icon']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Service Name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'base_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'icon': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Bootstrap icon name (e.g. camera)'}),
        }

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class ServicePortfolioForm(forms.ModelForm):
    image = forms.ImageField(widget=MultipleFileInput(attrs={'class': 'form-control', 'multiple': True}))
    
    class Meta:
        model = ServicePortfolio
        fields = ['image', 'caption']
        widgets = {
            'caption': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional: e.g., Grand Wedding Stage'}),
        }
