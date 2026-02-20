from django import forms

class CertificateUploadForm(forms.Form):
    certificate_image = forms.FileField()
