from django.shortcuts import render,redirect
from django.contrib.auth import login,logout,authenticate
from django.contrib.auth.models import User
from datetime import date, timedelta
from django.core.paginator import Paginator
from django.db.models import Q

from .ats_score import ats_score

from .models import JobPost,JobApplication,JobSeekerProfile,CompanyProfile
# Create your views here.
def home(request):
    return render(request, 'home.html')

def userlogin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:

            login(request, user)
            if user.is_superuser:
                return redirect('admin/login')
            elif user.is_staff:
                return redirect('dashboard')
            else:
                return redirect('jobseeker_dashboard')
        else:
            return render(request, 'login.html', {'error': 'Invalid username or password'})
    else:
        return render(request, 'login.html')

def userlogout(request):
    logout(request)
    return redirect('home')

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        if User.objects.filter(username=username).exists():
            return render(request, 'register.html', {'error': 'Username already exists'})
        elif password == confirm_password:
            user = User.objects.create_user(username=username, password=password)
            return redirect('login')
        else:
            return render(request, 'register.html', {'error': 'Passwords do not match'})
    else:
        return render(request, 'register.html')



def companydashboard(request):
    today = date.today()
    next_week = today + timedelta(days=7)

    # All jobs for this company (regardless of active/expired)
    jobs = JobPost.objects.filter(user=request.user).order_by('-posted_at')

    # Active = deadline today or later, and is_active=True
    active_jobs = jobs.filter(is_active=True, last_date__gte=today)

    # Expired = deadline passed (yesterday or earlier)
    expired_jobs = jobs.filter(last_date__lt=today)

    # Expiring soon = within next 7 days
    expiring_soon = jobs.filter(
        is_active=True,
        last_date__gte=today,
        last_date__lte=next_week
    )

    if request.method == "POST":
        JobPost.objects.create(
            user=request.user,
            job_title=request.POST.get("job_title"),
            company=request.POST.get("company"),
            location=request.POST.get("location"),
            job_type=request.POST.get("job_type"),
            experience=request.POST.get("experience"),
            description=request.POST.get("description"),
            last_date=request.POST.get("last_date"),
            salary=request.POST.get("salary"),
            is_active=True,
        )
        return redirect("dashboard")

    print("Active:", len(active_jobs))
    print("Expired:", len(expired_jobs))
    print("Expiring soon:", len(expiring_soon))

    return render(request, "company_dashboard.html", {
        "jobs": jobs,
        "active_jobs": active_jobs,
        "expired_jobs": expired_jobs,
        "expiring_soon": expiring_soon,
    })



def jobdetails(request, id):
    job = JobPost.objects.get(id=id)
    applied_job = JobApplication.objects.filter(job=job, job_seeker=request.user)
    return render(request, 'job_details.html', {'job': job, "today":date.today(), "applied_job":applied_job})

def deletejob(request, id):
    job = JobPost.objects.get(id=id)
    job.delete()
    return redirect(companydashboard)


def editjob(request, id):
    job = JobPost.objects.get(id=id)
    if request.method == "POST":
        job.job_title = request.POST.get("job_title")
        job.company = request.POST.get("company")
        job.location = request.POST.get("location")
        job.job_type = request.POST.get("job_type")
        job.experience = request.POST.get("experience")
        job.description = request.POST.get("description")
        job.last_date = request.POST.get("last_date")
        job.salary = request.POST.get("salary")
        job.save()
        return redirect(jobdetails, id)
    return redirect(jobdetails, id)

def active_status(requsert,id):
    job = JobPost.objects.get(id=id)
    job.is_active = not job.is_active
    job.save()
    return redirect(jobdetails, id)

def company_profile(request):
    if request.method == "POST":
        if CompanyProfile.objects.filter(user=request.user).exists():
            profile = CompanyProfile.objects.get(user=request.user)
            profile.phone = request.POST.get("phone")
            profile.address = request.POST.get("address")
            profile.company_name = request.POST.get("company_name")
            profile.company_description = request.POST.get("company_description")
            if request.FILES.get("company_logo"):
                profile.company_logo.delete()
                profile.company_logo = request.FILES.get("company_logo")
            profile.save()
        else:
            CompanyProfile.objects.create(
                user=request.user,
                phone=request.POST.get("phone"),
                address=request.POST.get("address"),
                company_name=request.POST.get("company_name"),
                company_description=request.POST.get("company_description"),
                company_logo=request.POST.get("company_logo"),
            )
        return redirect("company_profile")
    print(request.user.companyprofile.first())
    return render(request, 'company_profile.html', {'user': request.user})


def jobseeker_dashboard(request):
    # Get filter parameters from request
    query = request.GET.get('q', '')
    job_type = request.GET.get('job_type', '')
    experience = request.GET.get('experience', '')
    
    # Start with all active jobs
    jobs = JobPost.objects.filter(is_active=True).exclude(
        jobapplication__job_seeker=request.user
    )

    
    # Apply filters if provided
    if query:
        jobs = jobs.filter(
            Q(job_title__icontains=query) | 
            Q(company__icontains=query) | 
            Q(description__icontains=query)
        )
    
    if job_type:
        jobs = jobs.filter(job_type=job_type)
        
    if experience:
        jobs = jobs.filter(experience=experience)
    
    jobs = jobs.order_by('-posted_at')
    
    paginator = Paginator(jobs, 6)  # Show 6 jobs per page
    page_number = request.GET.get('page')
    job_posts = paginator.get_page(page_number)


    
    context = {
        'job_posts': job_posts,
    }
    return render(request, 'jobseeker_dashboard.html', context)

def apply_job(request):
    if request.method == "POST":
        resume = request.FILES.get("resume")

        joba = JobApplication.objects.create(
            job=JobPost.objects.get(id=request.POST.get("job_id")),
            job_seeker=request.user,
            resume=request.FILES.get("resume"),
        )
        
        ats = ats_score(joba.resume.path,JobPost.objects.get(id= request.POST.get('job_id')).description)
        print(ats)
        job = JobApplication.objects.get(id=joba.id)
        job.ats_score = ats
        job.save()
    return redirect("jobseeker_dashboard")


def jobseeker_profile(request):
    if request.method == "POST":
        if JobSeekerProfile.objects.filter(user=request.user).exists():
            profile = JobSeekerProfile.objects.get(user=request.user)
            profile.phone = request.POST.get("phone")
            profile.address = request.POST.get("address")
            if request.FILES.get("profile_picture"):
                profile.profile_picture.delete()
                profile.profile_picture = request.FILES.get("profile_picture")
            profile.save()
        else:
            JobSeekerProfile.objects.create(
                user=request.user,
                phone=request.POST.get("phone"),
                address=request.POST.get("address"),
                profile_picture=request.POST.get("profile_picture"),
            )
        return redirect("jobseeker_profile")
    return render(request, 'jobseekerprofile.html', {'user': request.user})