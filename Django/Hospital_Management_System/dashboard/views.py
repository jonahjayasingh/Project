from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, Q, F
from django.utils import timezone
from datetime import timedelta

from patients.models import Patient
from doctors.models import Doctor
from appointments.models import Appointment
from billing.models import Bill
from rooms.models import Admission, Bed
from pharmacy.models import Medicine

@login_required
def home_view(request):
    """
    Main dashboard view - redirects to role-specific dashboard
    """
    user = request.user
    
    if user.is_admin:
        return admin_dashboard(request)
    elif user.is_doctor:
        return doctor_dashboard(request)
    elif user.is_nurse:
        return nurse_dashboard(request)
    elif user.is_receptionist:
        return receptionist_dashboard(request)
    elif user.is_patient:
        return patient_dashboard(request)
    else:
        return render(request, 'dashboard/home.html')


@login_required
def admin_dashboard(request):
    """
    Admin dashboard with overall statistics
    """
    today = timezone.now().date()
    
    # Patient statistics
    total_patients = Patient.objects.count()
    active_patients = Patient.objects.filter(status='active').count()
    
    # Appointment statistics
    today_appointments = Appointment.objects.filter(appointment_date=today).count()
    pending_appointments = Appointment.objects.filter(status='scheduled').count()
    
    # Admission statistics
    active_admissions = Admission.objects.filter(status='admitted').count()
    
    # Bed statistics
    total_beds = Bed.objects.count()
    occupied_beds = Bed.objects.filter(is_occupied=True).count()
    available_beds = total_beds - occupied_beds
    
    # Revenue statistics (last 30 days)
    thirty_days_ago = today - timedelta(days=30)
    revenue = Bill.objects.filter(
        created_at__gte=thirty_days_ago,
        payment_status='paid'
    ).aggregate(
        total=Sum('consultation_fee') + Sum('medicine_charges') + Sum('room_charges') + Sum('lab_charges')
    )['total'] or 0
    
    # Pending bills
    pending_bills = Bill.objects.filter(payment_status__in=['pending', 'partial']).count()
    
    # Low stock medicines
    low_stock_medicines = Medicine.objects.filter(
        stock_quantity__lte=F('reorder_level')
    ).count()
    
    context = {
        'total_patients': total_patients,
        'active_patients': active_patients,
        'today_appointments': today_appointments,
        'pending_appointments': pending_appointments,
        'active_admissions': active_admissions,
        'total_beds': total_beds,
        'occupied_beds': occupied_beds,
        'available_beds': available_beds,
        'revenue': revenue,
        'pending_bills': pending_bills,
        'low_stock_medicines': low_stock_medicines,
    }
    
    return render(request, 'dashboard/admin_dashboard.html', context)


@login_required
def doctor_dashboard(request):
    """
    Doctor-specific dashboard
    """
    try:
        doctor = request.user.doctor_profile
    except:
        return render(request, 'dashboard/error.html', {'message': 'Doctor profile not found'})
    
    today = timezone.now().date()
    
    # Today's appointments
    today_appointments = Appointment.objects.filter(
        doctor=doctor,
        appointment_date=today
    ).select_related('patient__user').order_by('appointment_time')
    
    # Upcoming appointments
    upcoming_appointments = Appointment.objects.filter(
        doctor=doctor,
        appointment_date__gt=today,
        status='scheduled'
    ).select_related('patient__user').order_by('appointment_date', 'appointment_time')[:5]
    
    # Recent patients
    recent_patients = Patient.objects.filter(
        appointments__doctor=doctor
    ).distinct().order_by('-appointments__created_at')[:10]
    
    context = {
        'doctor': doctor,
        'today_appointments': today_appointments,
        'upcoming_appointments': upcoming_appointments,
        'recent_patients': recent_patients,
    }
    
    return render(request, 'dashboard/doctor_dashboard.html', context)


@login_required
def nurse_dashboard(request):
    """
    Nurse-specific dashboard
    """
    try:
        nurse = request.user.nurse_profile
    except:
        return render(request, 'dashboard/error.html', {'message': 'Nurse profile not found'})
    
    # Assigned patients
    assigned_patients = nurse.patient_assignments.filter(
        is_active=True
    ).select_related('patient__user')
    
    # Active admissions in nurse's department
    active_admissions = Admission.objects.filter(
        status='admitted',
        bed__room__beds__admissions__patient__nurse_assignments__nurse=nurse
    ).distinct()
    
    context = {
        'nurse': nurse,
        'assigned_patients': assigned_patients,
        'active_admissions': active_admissions,
    }
    
    return render(request, 'dashboard/nurse_dashboard.html', context)


@login_required
def receptionist_dashboard(request):
    """
    Receptionist dashboard
    """
    today = timezone.now().date()
    
    # Today's appointments
    today_appointments = Appointment.objects.filter(
        appointment_date=today
    ).select_related('patient__user', 'doctor__user').order_by('appointment_time')
    
    # Recent admissions
    recent_admissions = Admission.objects.filter(
        status='admitted'
    ).select_related('patient__user', 'bed__room').order_by('-admission_date')[:10]
    
    # Available beds
    available_beds = Bed.objects.filter(
        is_occupied=False,
        is_active=True
    ).select_related('room')
    
    context = {
        'today_appointments': today_appointments,
        'recent_admissions': recent_admissions,
        'available_beds': available_beds,
    }
    
    return render(request, 'dashboard/receptionist_dashboard.html', context)


@login_required
def patient_dashboard(request):
    """
    Patient-specific dashboard
    """
    try:
        patient = request.user.patient_profile
    except:
        return render(request, 'dashboard/error.html', {'message': 'Patient profile not found'})
    
    # Upcoming appointments
    upcoming_appointments = Appointment.objects.filter(
        patient=patient,
        appointment_date__gte=timezone.now().date(),
        status__in=['scheduled', 'confirmed']
    ).select_related('doctor__user').order_by('appointment_date', 'appointment_time')
    
    # Recent medical records
    recent_records = patient.medical_records.all().select_related('doctor__user').order_by('-created_at')[:5]
    
    # Recent bills
    recent_bills = patient.bills.all().order_by('-created_at')[:5]
    
    # Active prescriptions
    active_prescriptions = patient.prescriptions.filter(
        is_dispensed=False
    ).order_by('-created_at')
    
    context = {
        'patient': patient,
        'upcoming_appointments': upcoming_appointments,
        'recent_records': recent_records,
        'recent_bills': recent_bills,
        'active_prescriptions': active_prescriptions,
    }
    
    return render(request, 'dashboard/patient_dashboard.html', context)
