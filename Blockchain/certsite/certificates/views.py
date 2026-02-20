from django.shortcuts import render
from .forms import CertificateUploadForm
from .blockchain import register_certificate, verify_certificate

def register_view(request):
    tx_hash = None

    if request.method == "POST":
        form = CertificateUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.cleaned_data["certificate_image"]
            tx_hash = register_certificate(file)
    else:
        form = CertificateUploadForm()

    return render(request, "register.html", {
        "form": form,
        "tx_hash": tx_hash
    })


def verify_view(request):
    result = None

    if request.method == "POST":
        form = CertificateUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.cleaned_data["certificate_image"]
            result = verify_certificate(file)
    else:
        form = CertificateUploadForm()

    return render(request, "verify.html", {
        "form": form,
        "result": result
    })
