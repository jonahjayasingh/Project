from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.core.mail import send_mail
from django.conf import settings
from .forms import (
    PatientRegistrationForm, LoginForm, TestBookingForm, 
    LabRegistrationForm, LabTestForm, PaymentProofForm, ReportUploadForm
)
from .models import (
    PatientProfile, LabAssistant, TestBooking, LabTest, 
    LabPackage, LabReview, LabTechnician, LabWorkingHours, 
    LabHoliday, Notification, ActivityLog, ReportVersion, 
    SystemSetting, StaticPage
)
from datetime import datetime, timedelta
from django.utils import timezone
from django.db import models
from django.http import FileResponse, HttpResponseForbidden

def log_activity(request, action, details=""):
    ActivityLog.objects.create(
        user=request.user if request.user.is_authenticated else None,
        action=action,
        details=details,
        ip_address=request.META.get('REMOTE_ADDR')
    )

@login_required
def secure_report_serve(request, booking_id, version_id=None):
    booking = get_object_or_404(TestBooking, id=booking_id)
    
    # Permission Check
    can_access = False
    if request.user.is_superuser:
        can_access = True
    elif hasattr(request.user, 'lab_profile') and booking.lab == request.user.lab_profile:
        can_access = True
    elif hasattr(request.user, 'patient_profile') and booking.patient == request.user.patient_profile:
        can_access = True
        
    if not can_access:
        return HttpResponseForbidden("Not authorized to view this report.")
        
    if version_id:
        version = get_object_or_404(ReportVersion, id=version_id, booking=booking)
        file_path = version.report_file.path
    else:
        file_path = booking.report_file.path
        
    return FileResponse(open(file_path, 'rb'), content_type='application/pdf')


def home(request):
    return render(request, "home.html")

def static_page(request, slug):
    page = get_object_or_404(StaticPage, slug=slug, is_active=True)
    return render(request, "static_page.html", {'page': page})

def contact_us(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        # Log this as activity or send mail
        send_mail(
            f"Support Query: {subject}",
            f"From: {name} ({email})\n\n{message}",
            settings.DEFAULT_FROM_EMAIL,
            [settings.DEFAULT_FROM_EMAIL], # Send to admin
            fail_silently=True,
        )
        messages.success(request, "Your message has been sent. We will get back to you soon.")
        return redirect('contact_us')
    return render(request, "contact.html")

# --- Patient Views ---

def patient_register(request):
    if request.method == 'POST':
        form = PatientRegistrationForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['confirm_password']
            )
            print(form.cleaned_data["confirm_password"])
            patient = form.save(commit=False)
            patient.user = user
            patient.save()
            log_activity(request, "Patient Registration", f"New patient registered: {user.username}")
            login(request, user)
            return redirect('patient_dashboard')
    else:
        form = PatientRegistrationForm()
    return render(request, "patient_register.html", {'form': form})

def patient_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                if user.is_superuser:
                    login(request, user)
                    return redirect('admin_dashboard')
                elif hasattr(user, 'patient_profile'):
                    login(request, user)
                    return redirect('patient_dashboard')
                else:
                    form.add_error(None, "This account is not a patient account.")
            else:
                form.add_error(None, "Invalid username or password.")
    else:
        form = LoginForm()
    return render(request, "patient_login.html", {'form': form})

@login_required
def patient_dashboard(request):
    if not hasattr(request.user, 'patient_profile'):
        return redirect('home')
    patient = request.user.patient_profile
    bookings = patient.bookings.all().order_by('-created_at')
    
    upcoming = bookings.filter(booking_date__gte=datetime.now().date(), status__in=['Pending Approval', 'Confirmed']).order_by('booking_date')
    history = bookings.filter(Q(booking_date__lt=datetime.now().date()) | Q(status__in=['Completed', 'Cancelled'])).order_by('-booking_date')

    return render(request, "patient_dashboard.html", {
        'profile': patient,
        'upcoming': upcoming,
        'history': history,
        'bookings': bookings
    })

@login_required
def booking_receipt(request, booking_id):
    booking = get_object_or_404(TestBooking, id=booking_id)
    if not (request.user == booking.patient.user or request.user == booking.lab.user or request.user.is_superuser):
        return redirect('home')
    return render(request, "booking_receipt.html", {'booking': booking})

@login_required
def book_test(request):
    if not hasattr(request.user, 'patient_profile'):
        return redirect('home')
    if request.method == 'POST':
        form = TestBookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            lab = booking.lab
            
            # Capacity & Closure Checks
            if lab.is_emergency_closed:
                messages.error(request, f"Laboratory {lab.lab_name} is currently closed due to emergency.")
                return redirect('lab_discovery')
            
            daily_count = TestBooking.objects.filter(lab=lab, booking_date=booking.booking_date).exclude(status='Cancelled').count()
            if daily_count >= lab.daily_capacity:
                messages.error(request, f"Laboratory {lab.lab_name} has reached its daily booking capacity for {booking.booking_date}.")
                return redirect('book_test')

            booking.patient = request.user.patient_profile
            
            # Check for double booking
            if TestBooking.objects.filter(lab=booking.lab, booking_date=booking.booking_date, time_slot=booking.time_slot).exclude(status='Cancelled').exists():
                messages.error(request, "This time slot is already booked. Please choose another slot.")
            else:
                # Set test name and price at booking
                if booking.package:
                    booking.test_name = f"Package: {booking.package.package_name}"
                    booking.price_at_booking = booking.package.final_price
                elif booking.lab_test:
                    booking.test_name = booking.lab_test.test_name
                    booking.price_at_booking = booking.lab_test.price
                else:
                    messages.error(request, "Please select either a test or a package.")
                    return render(request, "book_test.html", {'form': form})
                    
                booking.save()
                log_activity(request, "Test Booking", f"Booked: {booking.test_name} at {lab.lab_name}")
                
                # Notification
                send_mail(
                    'Booking Received',
                    f'Your booking for {booking.test_name} at {booking.lab.lab_name} has been received. Please upload payment proof to confirm.',
                    settings.DEFAULT_FROM_EMAIL,
                    [request.user.email],
                    fail_silently=True,
                )
                
                messages.success(request, "Booking request submitted successfully!")
                return redirect('patient_dashboard')
    else:
        form = TestBookingForm()
    return render(request, "book_test.html", {'form': form})

@login_required
def upload_payment_proof(request, booking_id):
    booking = get_object_or_404(TestBooking, id=booking_id, patient=request.user.patient_profile)
    if request.method == 'POST':
        form = PaymentProofForm(request.POST, request.FILES, instance=booking)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.payment_status = 'Pending Verification'
            booking.save()
            messages.success(request, "Payment proof uploaded successfully.")
            return redirect('patient_dashboard')
    else:
        form = PaymentProofForm(instance=booking)
    return render(request, "upload_payment.html", {'form': form, 'booking': booking})

@login_required
def reschedule_booking(request, booking_id):
    booking = get_object_or_404(TestBooking, id=booking_id, patient=request.user.patient_profile)
    
    if booking.payment_status == 'Verified':
        messages.error(request, "Cannot reschedule after payment has been verified.")
        return redirect('patient_dashboard')

    if request.method == 'POST':
        form = TestBookingForm(request.POST, instance=booking)
        if form.is_valid():
            # Check for double booking
            if TestBooking.objects.filter(lab=booking.lab, booking_date=booking.booking_date, time_slot=booking.time_slot).exclude(id=booking.id).exclude(status='Cancelled').exists():
                messages.error(request, "New time slot is already booked.")
            else:
                form.save()
                messages.success(request, "Booking rescheduled successfully.")
                return redirect('patient_dashboard')
    else:
        form = TestBookingForm(instance=booking)
    return render(request, "reschedule_booking.html", {'form': form, 'booking': booking})

@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(TestBooking, id=booking_id, patient=request.user.patient_profile)

    if booking.payment_status == 'Verified':
        messages.error(request, "Cannot cancel after payment has been verified.")
        return redirect('patient_dashboard')

    if request.method == 'POST':
        reason = request.POST.get('reason', 'Patient requested cancellation.')
        booking.status = 'Cancelled'
        booking.cancellation_reason = reason
        booking.save()
        messages.success(request, "Booking cancelled successfully.")
        return redirect('patient_dashboard')
        
    return render(request, "confirm_cancel.html", {'booking': booking})

@login_required
def mark_no_show(request, booking_id):
    if not hasattr(request.user, 'lab_profile'):
        return redirect('home')
    booking = get_object_or_404(TestBooking, id=booking_id, lab=request.user.lab_profile)
    booking.is_no_show = True
    booking.status = 'Cancelled'
    booking.save()
    messages.info(request, f"Booking #{booking.id} marked as No-Show.")
    return redirect('lab_dashboard')

@login_required
def lab_discovery(request):
    if not hasattr(request.user, 'patient_profile'):
        return redirect('home')
        
    query = request.GET.get('q', '')
    pincode = request.GET.get('pincode', '')
    city = request.GET.get('city', '')
    only_packages = request.GET.get('only_packages') == 'on'
    min_rating = request.GET.get('min_rating')
    
    labs = LabAssistant.objects.filter(is_approved=True, is_active=True)
    
    if query:
        labs = labs.filter(Q(lab_name__icontains=query) | Q(bio__icontains=query))
    if pincode:
        labs = labs.filter(pincode=pincode)
    if city:
        labs = labs.filter(city__icontains=city)
    if only_packages:
        labs = labs.filter(packages__is_active=True).distinct()
    if min_rating:
        labs = labs.filter(rating_avg__gte=float(min_rating))
        
    return render(request, "lab_discovery.html", {
        'labs': labs,
        'query': query,
        'pincode': pincode,
        'city': city,
        'only_packages': only_packages,
        'min_rating': min_rating
    })

@login_required
def submit_review(request, booking_id):
    booking = get_object_or_404(TestBooking, id=booking_id, patient=request.user.patient_profile)
    lab = booking.lab
    
    if booking.status not in ['Confirmed', 'Completed']:
        messages.error(request, "You can only review confirmed or completed bookings.")
        return redirect('patient_dashboard')
        
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        
        # Check if booking already has a review
        if hasattr(booking, 'review'):
            messages.warning(request, "You have already reviewed this booking.")
            return redirect('patient_dashboard')

        LabReview.objects.create(
            lab=lab,
            patient=request.user.patient_profile,
            booking=booking,
            rating=rating,
            comment=comment
        )
        
        # Update lab average rating
        avg = lab.reviews.aggregate(models.Avg('rating'))['rating__avg']
        lab.rating_avg = avg or 0.0
        lab.save()
        
        messages.success(request, "Review submitted successfully.")
        return redirect('patient_dashboard')
        
    return render(request, "submit_review.html", {'lab': lab, 'booking': booking})

@login_required
def lab_reviews(request):
    if hasattr(request.user, 'lab_profile'):
        reviews = request.user.lab_profile.reviews.all().order_by('-created_at')
        if request.method == 'POST':
            review_id = request.POST.get('review_id')
            reply = request.POST.get('reply')
            review = get_object_or_404(LabReview, id=review_id, lab=request.user.lab_profile)
            review.lab_reply = reply
            review.save()
            messages.success(request, "Reply sent.")
            return redirect('lab_reviews')
        return render(request, "lab_reviews.html", {'reviews': reviews})
    return redirect('home')

@login_required
def manage_packages(request):
    if not hasattr(request.user, 'lab_profile'):
        return redirect('home')
    lab = request.user.lab_profile
    packages = lab.packages.all()
    tests = lab.available_tests.all()
    
    if request.method == 'POST':
        name = request.POST.get('name')
        desc = request.POST.get('description')
        price = request.POST.get('price')
        discount = request.POST.get('discount', 0)
        test_ids = request.POST.getlist('tests')
        
        package = LabPackage.objects.create(
            lab=lab,
            package_name=name,
            description=desc,
            price=price,
            discount_percentage=discount
        )
        package.tests.set(test_ids)
        messages.success(request, "Package created successfully.")
        return redirect('manage_packages')
        
    return render(request, "manage_packages.html", {'packages': packages, 'tests': tests})

@login_required
def edit_package(request, package_id):
    if not hasattr(request.user, 'lab_profile'):
        return redirect('home')
    package = get_object_or_404(LabPackage, id=package_id, lab=request.user.lab_profile)
    if request.method == 'POST':
        package.package_name = request.POST.get('name')
        package.description = request.POST.get('description')
        package.price = request.POST.get('price')
        package.discount_percentage = request.POST.get('discount', 0)
        test_ids = request.POST.getlist('tests')
        package.tests.set(test_ids)
        package.save()
        messages.success(request, "Package updated successfully.")
    return redirect('manage_packages')

@login_required
def delete_package(request, package_id):
    if request.method == 'POST':
        package = get_object_or_404(LabPackage, id=package_id, lab=request.user.lab_profile)
        package.delete()
        messages.success(request, "Package deleted.")
    return redirect('manage_packages')

@login_required
def lab_operations_config(request):
    if not hasattr(request.user, 'lab_profile'):
        return redirect('home')
    lab = request.user.lab_profile
    
    if request.method == 'POST':
        lab.daily_capacity = request.POST.get('daily_capacity', 50)
        lab.is_emergency_closed = 'is_emergency_closed' in request.POST
        lab.bio = request.POST.get('bio', '')
        lab.city = request.POST.get('city', '')
        lab.area = request.POST.get('area', '')
        lab.pincode = request.POST.get('pincode', '')
        if 'payment_qr_code' in request.FILES:
            lab.payment_qr_code = request.FILES['payment_qr_code']
        lab.save()
        messages.success(request, "Operational settings updated.")
        return redirect('lab_operations_config')
        
    return render(request, "lab_operations_config.html", {'lab': lab})

@login_required
def manage_staff(request):
    if not hasattr(request.user, 'lab_profile'):
        return redirect('home')
    lab = request.user.lab_profile
    staff = lab.technicians.all()
    
    if request.method == 'POST':
        name = request.POST.get('name')
        spec = request.POST.get('specialization')
        LabTechnician.objects.create(lab=lab, name=name, specialization=spec)
        messages.success(request, "Technician added.")
        return redirect('manage_staff')
        
    return render(request, "manage_staff.html", {'staff': staff})

@login_required
def edit_staff(request, staff_id):
    if not hasattr(request.user, 'lab_profile'):
        return redirect('home')
    staff = get_object_or_404(LabTechnician, id=staff_id, lab=request.user.lab_profile)
    if request.method == 'POST':
        staff.name = request.POST.get('name')
        staff.specialization = request.POST.get('specialization')
        staff.is_active = 'is_active' in request.POST
        staff.save()
        messages.success(request, "Technician updated successfully.")
    return redirect('manage_staff')

@login_required
def delete_staff(request, staff_id):
    if request.method == 'POST':
        staff = get_object_or_404(LabTechnician, id=staff_id, lab=request.user.lab_profile)
        staff.delete()
        messages.success(request, "Technician removed.")
    return redirect('manage_staff')

@login_required
def assign_technician(request, booking_id):
    if not hasattr(request.user, 'lab_profile'):
        return redirect('home')
    booking = get_object_or_404(TestBooking, id=booking_id, lab=request.user.lab_profile)
    
    if request.method == 'POST':
        tech_id = request.POST.get('technician')
        notes = request.POST.get('internal_notes', '')
        if tech_id:
            booking.technician = get_object_or_404(LabTechnician, id=tech_id, lab=request.user.lab_profile)
        booking.internal_notes = notes
        booking.save()
        messages.success(request, "Technician and notes updated.")
    return redirect('lab_dashboard')

# --- Laboratory Registration ---

def lab_register(request):
    if request.method == 'POST':
        form = LabRegistrationForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['confirm_password']
            )
            lab = form.save(commit=False)
            lab.user = user
            lab.save()
            messages.success(request, "Registration successful! Please wait for admin approval.")
            return redirect('lab_login')
    else:
        form = LabRegistrationForm()
    return render(request, "lab_register.html", {'form': form})

def lab_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                if user.is_superuser:
                    login(request, user)
                    return redirect('admin_dashboard')
                elif hasattr(user, 'lab_profile'):
                    lab = user.lab_profile
                    if not lab.is_active:
                        messages.error(request, "Your account has been temporarily disabled.")
                        return redirect('lab_login')
                    if lab.is_approved:
                        login(request, user)
                        log_activity(request, "Lab Login", f"Lab user {user.username} logged in")
                        return redirect('lab_dashboard')
                    else:
                        messages.warning(request, "Your account is pending approval.")
                        return redirect('lab_login')
                else:
                    form.add_error(None, "This account is not a lab account.")
            else:
                form.add_error(None, "Invalid username or password.")
    else:
        form = LoginForm()
    return render(request, "lab_login.html", {'form': form})

@login_required
def lab_dashboard(request):
    if not hasattr(request.user, 'lab_profile'):
        return redirect('home')
    lab = request.user.lab_profile
    bookings = TestBooking.objects.filter(lab=lab).order_by('-created_at')
    
    # Summary Stats
    total_bookings = bookings.count()
    pending_tasks = bookings.exclude(status__in=['Completed', 'Cancelled']).count()
    completed_today = bookings.filter(status='Completed', updated_at__date=datetime.now().date()).count()
    today_appointments = bookings.filter(booking_date=datetime.now().date()).order_by('time_slot')

    return render(request, "lab_dashboard.html", {
        'bookings': bookings,
        'total_bookings': total_bookings,
        'pending_tasks': pending_tasks,
        'completed_today': completed_today,
        'today_appointments': today_appointments
    })

@login_required
def lab_patient_list(request):
    if not hasattr(request.user, 'lab_profile'):
        return redirect('home')
    lab = request.user.lab_profile
    query = request.GET.get('q', '')
    
    patients = PatientProfile.objects.filter(bookings__lab=lab).distinct()
    
    if query:
        patients = patients.filter(
            Q(full_name__icontains=query) | 
            Q(whatsapp_number__icontains=query) | 
            Q(user__email__icontains=query)
        )
        
    return render(request, "lab_patient_list.html", {'patients': patients, 'query': query})

@login_required
def manage_lab_tests(request):
    if not hasattr(request.user, 'lab_profile'):
        return redirect('home')
    lab = request.user.lab_profile
    tests = lab.available_tests.all()
    if request.method == 'POST':
        form = LabTestForm(request.POST)
        if form.is_valid():
            test = form.save(commit=False)
            test.lab = lab
            test.save()
            messages.success(request, "Test added successfully.")
            return redirect('manage_lab_tests')
    else:
        form = LabTestForm()
    return render(request, "manage_tests.html", {'form': form, 'tests': tests})

@login_required
def edit_lab_test(request, test_id):
    if not hasattr(request.user, 'lab_profile'):
        return redirect('home')
    lab = request.user.lab_profile
    test = get_object_or_404(LabTest, id=test_id, lab=lab)
    if request.method == 'POST':
        form = LabTestForm(request.POST, instance=test)
        if form.is_valid():
            form.save()
            messages.success(request, "Test updated successfully.")
            return redirect('manage_lab_tests')
    else:
        form = LabTestForm(instance=test)
    return render(request, "edit_test.html", {'form': form, 'test': test})

@login_required
def delete_lab_test(request, test_id):
    if not hasattr(request.user, 'lab_profile'):
        return redirect('home')
    if request.method == 'POST':
        lab = request.user.lab_profile
        test = get_object_or_404(LabTest, id=test_id, lab=lab)
        test.delete()
        messages.success(request, "Test deleted successfully.")
    return redirect('manage_lab_tests')

@login_required
def update_booking_status(request, booking_id):
    booking = get_object_or_404(TestBooking, id=booking_id, lab=request.user.lab_profile)
    new_status = request.POST.get('status')
    if new_status in [choice[0] for choice in TestBooking.STATUS_CHOICES]:
        booking.status = new_status
        booking.save()
        messages.success(request, f"Status updated to {new_status}")
    return redirect('lab_dashboard')

@login_required
def verify_payment(request, booking_id):
    booking = get_object_or_404(TestBooking, id=booking_id, lab=request.user.lab_profile)
    action = request.POST.get('action')
    if action == 'verify':
        booking.payment_status = 'Verified'
        booking.status = 'Confirmed'
        send_mail(
            'Payment Verified',
            f'Your payment for {booking.test_name} has been verified. Your booking is now confirmed.',
            settings.DEFAULT_FROM_EMAIL,
            [booking.patient.user.email],
            fail_silently=True,
        )
        messages.success(request, "Payment verified and booking confirmed.")
    elif action == 'reject':
        booking.payment_status = 'Rejected'
        booking.payment_rejection_reason = request.POST.get('reason', 'Invalid proof.')
        send_mail(
            'Payment Rejected',
            f'Your payment proof for {booking.test_name} was rejected. Reason: {booking.payment_rejection_reason}. Please re-upload.',
            settings.DEFAULT_FROM_EMAIL,
            [booking.patient.user.email],
            fail_silently=True,
        )
        messages.warning(request, "Payment proof rejected.")
    booking.save()
    return redirect('lab_dashboard')

@login_required
def upload_report(request, booking_id):
    booking = get_object_or_404(TestBooking, id=booking_id, lab=request.user.lab_profile)
    if request.method == 'POST':
        form = ReportUploadForm(request.POST, request.FILES, instance=booking)
        if form.is_valid():
            report_file = request.FILES.get('report_file')
            if report_file:
                # Create history version before updating
                next_version = booking.versions.count() + 1
                ReportVersion.objects.create(
                    booking=booking,
                    report_file=report_file,
                    version_number=next_version,
                    uploaded_by=request.user,
                    notes=request.POST.get('report_remarks', '')
                )
            
            form.save()
            
            # Create Notification
            Notification.objects.create(
                user=booking.patient.user,
                message=f"New report version (V{booking.versions.count()}) uploaded for your test: {booking.test_name}",
                type='Report'
            )

            if booking.is_report_final:
                booking.status = 'Completed'
                booking.save()
                send_mail(
                    'Test Report Available',
                    f'Your final test report for {booking.test_name} is now available in your dashboard.',
                    settings.DEFAULT_FROM_EMAIL,
                    [booking.patient.user.email],
                    fail_silently=True,
                )
            messages.success(request, f"Report (V{booking.versions.count()}) uploaded successfully.")
            log_activity(request, "Report Upload", f"Uploaded report V{booking.versions.count()} for Booking #{booking.id}")
            return redirect('lab_dashboard')
    else:
        form = ReportUploadForm(instance=booking)
    return render(request, "upload_report.html", {'form': form, 'booking': booking})

@login_required
def report_history(request, booking_id):
    # Visible to both lab and patient
    if hasattr(request.user, 'lab_profile'):
        booking = get_object_or_404(TestBooking, id=booking_id, lab=request.user.lab_profile)
    elif hasattr(request.user, 'patient_profile'):
        booking = get_object_or_404(TestBooking, id=booking_id, patient=request.user.patient_profile)
    else:
        return redirect('home')
        
    versions = booking.versions.all().order_by('-version_number')
    return render(request, "report_history.html", {'booking': booking, 'versions': versions})

@login_required
def notifications_list(request):
    notifications = request.user.notifications.all().order_by('-created_at')
    return render(request, "notifications.html", {'notifications': notifications})

@login_required
def mark_notification_read(request, n_id):
    notification = get_object_or_404(Notification, id=n_id, user=request.user)
    notification.is_read = True
    notification.save()
    return redirect('notifications_list')

@user_passes_test(lambda u: u.is_superuser)
def admin_activity_logs(request):
    logs = ActivityLog.objects.all().order_by('-timestamp')
    paginator = Paginator(logs, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, "admin_activity_logs.html", {'page_obj': page_obj})

# --- End of Views ---

@user_passes_test(lambda u: u.is_superuser)
def admin_dashboard(request):
    query = request.GET.get('search', '')
    
    total_patients = PatientProfile.objects.count()
    total_labs = LabAssistant.objects.count()
    pending_labs = LabAssistant.objects.filter(is_approved=False).count()
    total_bookings = TestBooking.objects.count()

    # Trends (Last 6 Months)
    six_months_ago = timezone.now() - timedelta(days=180)
    booking_trends = TestBooking.objects.filter(created_at__gte=six_months_ago).extra(
        select={'month': "strftime('%%Y-%%m', created_at)"}
    ).values('month').annotate(count=Count('id')).order_by('month')

    # Popular Tests
    popular_tests = TestBooking.objects.values('test_name').annotate(
        count=Count('id')).order_by('-count')[:5]

    # Lab Performance
    lab_performance = LabAssistant.objects.annotate(
        booking_count=Count('bookings'),
        avg_rating=models.Avg('reviews__rating')
    ).order_by('-booking_count')[:5]

    recent_activities = TestBooking.objects.all().order_by('-created_at')[:10]
    
    labs = LabAssistant.objects.all().order_by('-created_at')
    if query:
        labs = labs.filter(Q(lab_name__icontains=query) | Q(license_number__icontains=query))

    return render(request, "admin_dashboard.html", {
        'total_patients': total_patients,
        'total_labs': total_labs,
        'pending_labs': pending_labs,
        'total_bookings': total_bookings,
        'recent_activities': recent_activities,
        'labs': labs,
        'booking_trends': booking_trends,
        'popular_tests': popular_tests,
        'lab_performance': lab_performance,
    })

@user_passes_test(lambda u: u.is_superuser)
def system_settings(request):
    settings = SystemSetting.objects.all()
    if request.method == 'POST':
        for key, value in request.POST.items():
            if key.startswith('setting_'):
                setting_key = key.replace('setting_', '')
                SystemSetting.objects.filter(key=setting_key).update(value=value)
        messages.success(request, "Settings updated successfully.")
        return redirect('system_settings')
    return render(request, "admin_settings.html", {'settings': settings})

@user_passes_test(lambda u: u.is_superuser)
def export_analytics(request):
    import csv
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="lms_analytics.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Type', 'Name', 'Metric'])
    
    # Popular Tests
    for test in TestBooking.objects.values('test_name').annotate(count=Count('id')).order_by('-count'):
        writer.writerow(['Test', test['test_name'], test['count']])
        
    # Lab Performance
    for lab in LabAssistant.objects.annotate(count=Count('bookings')):
        writer.writerow(['Laboratory', lab.lab_name, lab.count])
        
    return response

@user_passes_test(lambda u: u.is_superuser)
def approve_lab(request, lab_id):
    lab = get_object_or_404(LabAssistant, id=lab_id)
    lab.is_approved = True
    lab.is_active = True
    lab.save()
    messages.success(request, f"Lab {lab.lab_name} approved successfully.")
    return redirect('admin_dashboard')

@user_passes_test(lambda u: u.is_superuser)
def toggle_lab_status(request, lab_id):
    lab = get_object_or_404(LabAssistant, id=lab_id)
    lab.is_active = not lab.is_active
    lab.save()
    status = "enabled" if lab.is_active else "disabled"
    messages.info(request, f"Lab {lab.lab_name} has been {status}.")
    return redirect('admin_dashboard')

@user_passes_test(lambda u: u.is_superuser)
def admin_user_management(request):
    patients = PatientProfile.objects.all()
    labs = LabAssistant.objects.all()
    return render(request, "admin_users.html", {'patients': patients, 'labs': labs})

# --- Common Views ---

def load_tests(request):
    lab_id = request.GET.get('lab')
    tests = LabTest.objects.filter(lab_id=lab_id).order_by('test_name')
    return render(request, "test_dropdown_list_options.html", {'tests': tests})

def load_packages(request):
    lab_id = request.GET.get('lab')
    packages = LabPackage.objects.filter(lab_id=lab_id, is_active=True).order_by('package_name')
    return render(request, "package_dropdown_list_options.html", {'packages': packages})

def user_logout(request):
    logout(request)
    return redirect('home')
