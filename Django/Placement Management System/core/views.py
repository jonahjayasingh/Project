from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User, StudentProfile, CompanyProfile

def home(request):
    return render(request, 'core/home.html')

def student_register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        register_number = request.POST.get('register_number')
        year_of_study = request.POST.get('year_of_study')
        department = request.POST.get('department')

        # Check for final year (assuming 4 is final year)
        if int(year_of_study) != 4:
            messages.error(request, "Only final year students can register.")
            return render(request, 'core/register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return render(request, 'core/register.html')

        user = User.objects.create_user(username=username, password=password, role='student')
        StudentProfile.objects.create(
            user=user,
            register_number=register_number,
            year_of_study=year_of_study,
            department=department,
            is_approved=False
        )
        messages.success(request, "Registration successful! Please wait for admin approval to access your dashboard.")
        return redirect('userlogin')
    
    return render(request, 'core/register.html')

def userlogin(request):
    # If user is already authenticated, redirect to their dashboard
    if request.user.is_authenticated:
        if request.user.role == 'student':
            return redirect('student_dashboard')
        elif request.user.role == 'admin':
            return redirect('admin_dashboard')
        elif request.user.role == 'company':
            return redirect('company_dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            
            # Redirect based on user's role (automatically detected)
            if user.role == 'student':
                return redirect('student_dashboard')
            elif user.role == 'admin':
                return redirect('admin_dashboard')
            elif user.role == 'company':
                return redirect('company_dashboard')
            else:
                messages.error(request, "Invalid user role.")
                logout(request)
        else:
            messages.error(request, "Invalid username or password.")
    
    return render(request, 'core/userlogin.html')

@login_required
def student_dashboard(request):
    if request.user.role != 'student':
        return redirect('userlogin')
    profile = request.user.student_profile
    if not profile.is_approved:
        return render(request, 'core/pending_approval.html', {'profile': profile})
    return render(request, 'core/student_dashboard.html', {'profile': profile})

@login_required
def admin_dashboard(request):
    if request.user.role != 'admin':
        return redirect('userlogin')
    student_count = StudentProfile.objects.count()
    company_count = CompanyProfile.objects.count()
    return render(request, 'core/admin_dashboard.html', {
        'student_count': student_count,
        'company_count': company_count
    })

@login_required
def students_list(request):
    if request.user.role != 'admin':
        return redirect('userlogin')
    students = StudentProfile.objects.select_related('user').all()
    return render(request, 'core/students.html', {'students': students})

@login_required
def approve_student(request, student_id):
    if request.user.role != 'admin':
        return redirect('userlogin')
    try:
        profile = StudentProfile.objects.get(id=student_id)
        profile.is_approved = not profile.is_approved
        profile.save()
        status = "approved" if profile.is_approved else "unapproved"
        messages.success(request, f"Student {profile.user.username} has been {status}.")
    except StudentProfile.DoesNotExist:
        messages.error(request, "Student not found.")
    return redirect('students_list')

@login_required
def company_dashboard(request):
    if request.user.role != 'company':
        return redirect('userlogin')
    profile = request.user.company_profile
    if not profile.is_approved:
        return render(request, 'core/company_pending_approval.html', {'profile': profile})
    return render(request, 'core/company_dashboard.html', {'profile': profile})

def company_register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        company_name = request.POST.get('company_name')
        industry = request.POST.get('industry')
        location = request.POST.get('location')
        contact_email = request.POST.get('contact_email')
        contact_phone = request.POST.get('contact_phone')

        # Check if passwords match
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'core/company_register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return render(request, 'core/company_register.html')

        user = User.objects.create_user(username=username, password=password, role='company')
        CompanyProfile.objects.create(
            user=user,
            company_name=company_name,
            industry=industry,
            location=location,
            contact_email=contact_email,
            contact_phone=contact_phone,
            is_approved=False
        )
        messages.success(request, "Registration successful! Please wait for admin approval to access your dashboard.")
        return redirect('userlogin')
    
    return render(request, 'core/company_register.html')

@login_required
def companies_list(request):
    if request.user.role != 'admin':
        return redirect('userlogin')
    companies = CompanyProfile.objects.select_related('user').all()
    return render(request, 'core/companies.html', {'companies': companies})

@login_required
def approve_company(request, company_id):
    if request.user.role != 'admin':
        return redirect('userlogin')
    try:
        profile = CompanyProfile.objects.get(id=company_id)
        profile.is_approved = not profile.is_approved
        profile.save()
        status = "approved" if profile.is_approved else "unapproved"
        messages.success(request, f"Company {profile.company_name} has been {status}.")
    except CompanyProfile.DoesNotExist:
        messages.error(request, "Company not found.")
    return redirect('companies_list')

def logout_view(request):
    logout(request)
    return redirect('userlogin')
