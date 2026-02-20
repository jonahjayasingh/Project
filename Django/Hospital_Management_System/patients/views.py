from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Patient, PatientDocument
from .forms import PatientUserForm, PatientProfileForm, PatientDocumentForm
from accounts.models import User

@login_required
def patient_list(request):
    """List all patients with search and filter"""
    patients = Patient.objects.select_related('user').all()
    
    # Search
    search_query = request.GET.get('search', '')
    if search_query:
        patients = patients.filter(
            Q(patient_id__icontains=search_query) |
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(user__email__icontains=search_query)
        )
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        patients = patients.filter(status=status_filter)
    
    # Pagination
    paginator = Paginator(patients, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
    }
    return render(request, 'patients/patient_list.html', context)


@login_required
def patient_detail(request, pk):
    """View patient details"""
    patient = get_object_or_404(Patient.objects.select_related('user'), pk=pk)
    documents = patient.documents.all().order_by('-uploaded_at')
    appointments = patient.appointments.select_related('doctor__user').order_by('-appointment_date')[:10]
    medical_records = patient.medical_records.select_related('doctor__user').order_by('-created_at')[:10]
    bills = patient.bills.all().order_by('-created_at')[:10]
    
    context = {
        'patient': patient,
        'documents': documents,
        'appointments': appointments,
        'medical_records': medical_records,
        'bills': bills,
    }
    return render(request, 'patients/patient_detail.html', context)


@login_required
def patient_create(request):
    """Create new patient"""
    if request.method == 'POST':
        user_form = PatientUserForm(request.POST)
        profile_form = PatientProfileForm(request.POST)
        
        if user_form.is_valid() and profile_form.is_valid():
            # Create user
            user = user_form.save(commit=False)
            user.role = 'patient'
            password = user_form.cleaned_data.get('password')
            if password:
                user.set_password(password)
            else:
                user.set_password('patient123')  # Default password
            user.save()
            
            # Create patient profile
            patient = profile_form.save(commit=False)
            patient.user = user
            patient.save()
            
            messages.success(request, f'Patient {patient.patient_id} created successfully!')
            return redirect('patients:patient_detail', pk=patient.pk)
    else:
        user_form = PatientUserForm()
        profile_form = PatientProfileForm()
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'action': 'Create'
    }
    return render(request, 'patients/patient_form.html', context)


@login_required
def patient_update(request, pk):
    """Update patient information"""
    patient = get_object_or_404(Patient, pk=pk)
    
    if request.method == 'POST':
        user_form = PatientUserForm(request.POST, instance=patient.user)
        profile_form = PatientProfileForm(request.POST, instance=patient)
        
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)
            password = user_form.cleaned_data.get('password')
            if password:
                user.set_password(password)
            user.save()
            
            profile_form.save()
            
            messages.success(request, f'Patient {patient.patient_id} updated successfully!')
            return redirect('patients:patient_detail', pk=patient.pk)
    else:
        user_form = PatientUserForm(instance=patient.user)
        profile_form = PatientProfileForm(instance=patient)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'patient': patient,
        'action': 'Update'
    }
    return render(request, 'patients/patient_form.html', context)


@login_required
def patient_delete(request, pk):
    """Delete patient"""
    patient = get_object_or_404(Patient, pk=pk)
    
    if request.method == 'POST':
        patient_id = patient.patient_id
        user = patient.user
        patient.delete()
        user.delete()
        messages.success(request, f'Patient {patient_id} deleted successfully!')
        return redirect('patients:patient_list')
    
    context = {'patient': patient}
    return render(request, 'patients/patient_confirm_delete.html', context)


@login_required
def patient_document_upload(request, patient_pk):
    """Upload document for patient"""
    patient = get_object_or_404(Patient, pk=patient_pk)
    
    if request.method == 'POST':
        form = PatientDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.patient = patient
            document.uploaded_by = request.user
            document.save()
            messages.success(request, 'Document uploaded successfully!')
            return redirect('patients:patient_detail', pk=patient.pk)
    else:
        form = PatientDocumentForm()
    
    context = {
        'form': form,
        'patient': patient
    }
    return render(request, 'patients/document_upload.html', context)


@login_required
def patient_document_delete(request, pk):
    """Delete patient document"""
    document = get_object_or_404(PatientDocument, pk=pk)
    patient_pk = document.patient.pk
    
    if request.method == 'POST':
        document.delete()
        messages.success(request, 'Document deleted successfully!')
        return redirect('patients:patient_detail', pk=patient_pk)
    
    context = {'document': document}
    return render(request, 'patients/document_confirm_delete.html', context)
