from django import forms
from django.contrib.auth.models import User
from .models import PatientProfile, TestBooking, LabAssistant, LabTest, LabPackage

class PatientRegistrationForm(forms.ModelForm):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    full_name = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}))
    whatsapp_number = forms.CharField(max_length=15, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'WhatsApp Number'}))
    address = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Address', 'rows': 3}))
    age = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Age'}))
    gender = forms.ChoiceField(choices=PatientProfile.GENDER_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password', 'id': 'password-field'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password', 'id': 'confirm-password-field'}))

    class Meta:
        model = PatientProfile
        fields = ['full_name', 'whatsapp_number', 'address', 'age', 'gender']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

class LabRegistrationForm(forms.ModelForm):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password', 'id': 'password-field_lab'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password', 'id': 'confirm-password-field_lab'}))

    class Meta:
        model = LabAssistant
        fields = ['lab_name', 'license_number']
        widgets = {
            'lab_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Laboratory Name'}),
            'license_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'License Number'}),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

class TestBookingForm(forms.ModelForm):
    TIME_SLOTS = [
    ('09:00', '09:00 AM'),
    ('09:30', '09:30 AM'),
    ('10:00', '10:00 AM'),
    ('10:30', '10:30 AM'),
    ('11:00', '11:00 AM'),
    ('11:30', '11:30 AM'),
    ('12:00', '12:00 PM'),
    ('12:30', '12:30 PM'),
    ('13:00', '01:00 PM'),
    ('13:30', '01:30 PM'),
    ('14:00', '02:00 PM'),
    ('14:30', '02:30 PM'),
    ('15:00', '03:00 PM'),
    ('15:30', '03:30 PM'),
    ('16:00', '04:00 PM'),
    ('16:30', '04:30 PM'),
    ('17:00', '05:00 PM'),
]

    time_slot = forms.ChoiceField(choices=TIME_SLOTS, widget=forms.Select(attrs={'class': 'form-select'}))

    class Meta:
        model = TestBooking
        fields = ['lab', 'lab_test', 'package', 'booking_date', 'time_slot']
        widgets = {
            'lab': forms.Select(attrs={'class': 'form-select', 'id': 'lab-select'}),
            'lab_test': forms.Select(attrs={'class': 'form-select', 'id': 'test-select'}),
            'package': forms.Select(attrs={'class': 'form-select', 'id': 'package-select'}),
            'booking_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['lab'].queryset = LabAssistant.objects.filter(is_approved=True)
        self.fields['lab'].empty_label = "Select Laboratory"
        self.fields['lab_test'].queryset = LabTest.objects.none()
        self.fields['package'].queryset = LabPackage.objects.none()
        self.fields['lab_test'].required = False
        self.fields['package'].required = False

        if 'lab' in self.data:
            try:
                lab_id = int(self.data.get('lab'))
                self.fields['lab_test'].queryset = LabTest.objects.filter(lab_id=lab_id)
                self.fields['package'].queryset = LabPackage.objects.filter(lab_id=lab_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.lab:
            self.fields['lab_test'].queryset = self.instance.lab.available_tests.all()
            self.fields['package'].queryset = self.instance.lab.packages.all()

class LabTestForm(forms.ModelForm):
    class Meta:
        model = LabTest
        fields = ['test_name', 'description', 'price']
        widgets = {
            'test_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Test Name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Description', 'rows': 3}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Price'}),
        }

class PaymentProofForm(forms.ModelForm):
    class Meta:
        model = TestBooking
        fields = ['payment_proof']
        widgets = {
            'payment_proof': forms.FileInput(attrs={'class': 'form-control'}),
        }

class ReportUploadForm(forms.ModelForm):
    class Meta:
        model = TestBooking
        fields = ['report_file', 'report_remarks', 'is_report_final']
        widgets = {
            'report_file': forms.FileInput(attrs={'class': 'form-control'}),
            'report_remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_report_final': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))
