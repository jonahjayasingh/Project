from django import forms

class PredictionForm(forms.Form):
    SEX_CHOICES = [
        ('Female', 'Female'),
        ('Male', 'Male'),
    ]
    
    age = forms.IntegerField(label='Age', min_value=18, max_value=74, widget=forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '18 - 74'}))
    sex = forms.ChoiceField(label='Sex', choices=SEX_CHOICES, widget=forms.Select(attrs={'class': 'form-input'}))
    heart_rate = forms.FloatField(label='Heart Rate (bpm)', min_value=40.0, max_value=150.0, widget=forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '40 - 150'}))
    systolic_bp = forms.FloatField(label='Systolic Blood Pressure', min_value=80.0, max_value=200.0, widget=forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '80 - 200'}))
    diastolic_bp = forms.FloatField(label='Diastolic Blood Pressure', min_value=40.0, max_value=120.0, widget=forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '40 - 120'}))
    respiratory_rate = forms.FloatField(label='Respiratory Rate', min_value=6.0, max_value=30.0, widget=forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '6 - 30'}))
    oxygen_saturation = forms.FloatField(label='Oxygen Saturation (%)', min_value=85.0, max_value=100.0, widget=forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '85 - 100'}))
    body_temperature = forms.FloatField(label='Body Temperature (°C)', min_value=34.0, max_value=41.0, widget=forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '34 - 41'}))
    blood_pH = forms.FloatField(label='Blood pH', min_value=7.0, max_value=7.7, widget=forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '7.0 - 7.7'}))
    ALT = forms.FloatField(label='ALT (Alanine Aminotransferase)', min_value=5.0, max_value=100.0, widget=forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '5 - 100'}))
    AST = forms.FloatField(label='AST (Aspartate Aminotransferase)', min_value=5.0, max_value=100.0, widget=forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '5 - 100'}))
    creatinine = forms.FloatField(label='Creatinine', min_value=0.3, max_value=2.5, widget=forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '0.3 - 2.5'}))
    glucose = forms.FloatField(label='Glucose', min_value=40.0, max_value=200.0, widget=forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '40 - 200'}))
    WBC_count = forms.FloatField(label='WBC Count', min_value=1.0, max_value=16.0, widget=forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '1 - 16'}))
    hours_since_use = forms.FloatField(label='Hours Since Use', min_value=0.0, max_value=72.0, widget=forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '0 - 72'}))
