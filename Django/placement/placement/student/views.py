from django.shortcuts import render,redirect
from app.models import UserPermission
from .models import StudentDetails
from django.contrib.auth.models import User
from django.contrib import messages
from company.models import JobDetails,JobApplication
from app.models import DegreeSpecialization,Notification
import json
from django.http import HttpResponse
from django_htmx.http import trigger_client_event
from teacher.models import Training


# Create your views here.
def dashboard(request):
    if request.method == 'POST':
        job_id = request.POST.get("job_id")
        cover_letter = request.POST.get("cover_letter")
        availability = request.POST.get('availability')
        cgpa_required = request.POST.get('cgpa_met') == 'yes'
        confirm_info = request.POST.get('confirm_info') == 'on'
        job = JobDetails.objects.get(id=job_id)
        student = StudentDetails.objects.get(user= request.user)
        if JobApplication.objects.filter(job=job,user=student).exists():
            messages.error(request,"You have already applied for this job")
            return redirect("student:student")
        
        JobApplication(job=job,user=student,cover_letter=cover_letter,available_to_work_in=availability,cgpa_required=cgpa_required,confirm_info=confirm_info).save()
        messages.success(request,"Your Application has been submitted")
        return redirect("student:student")
        
    student = StudentDetails.objects.get(user= request.user)
    try:
        jobs = JobDetails.objects.filter(
            cgpa_threshold__lte=student.cgpa,
            is_active=True
        ).exclude(
            applications__user=student
        )
        locations =JobDetails.objects.filter(
            cgpa_threshold__lte=student.cgpa,
            is_active=True
        ).exclude(
            applications__user=student
        ).values_list("location",flat=True).distinct()
    except:
        
        jobs = None
        locations = None
        
    print(locations)
    print(jobs)
    content = {
        "user_data" : UserPermission.objects.get(user=request.user),
        "jobs" : jobs,
        "student" : student,
        "notifications" : Notification.objects.filter(user=request.user).order_by("-id"),
        "notifications_count" : Notification.objects.filter(user=request.user,is_read=False).count(),
        "location": locations

    }
    return render(request,"student/dashboard.html",content)

def profile(request):
    if request.method == 'POST':
        try:
            img = request.FILES.get("profile_picture")
        except:
            img = None
        name = request.POST.get("name")
        email = request.POST.get("email")
        ph_no = request.POST.get("phone")
        dob = request.POST.get("date_of_birth")
        gender = request.POST.get("gender")
        blood_group = request.POST.get("blood_group")
        address =  request.POST.get("address")
        course = request.POST.get("course")
        branch = request.POST.get("branch")
        year = request.POST.get("year")
        semester = request.POST.get("sem")
        roll_no = request.POST.get('roll_no')
        reg_no =  request.POST.get("reg_no")
        cgpa = request.POST.get("cgpa")
        is_edit = request.POST.get('hide')
        resume = None if request.FILES.get("resume") == "" else request.FILES.get("resume")
        job_title = request.POST.get("job_title")
        company_name = request.POST.get("company_name")
        company_location = request.POST.get("company_location")
        salary = 0 if request.POST.get("salary") == "" else request.POST.get("salary")
        user = User.objects.get(username=request.user)
        print(resume)
        if is_edit is None:
            StudentDetails(user=user,name=name,email=email,phone=ph_no,address=address,date_of_birth=dob,gender=gender,blood_group=blood_group,profile_picture=img,course=course,branch=branch,year=year,sem= semester,roll_no=roll_no,reg_no=reg_no,cgpa=cgpa,resume=resume,job_title=job_title,company_name=company_name,company_location=company_location,salary=salary).save()
            messages.success(request,"Your Profile has been added")
            return redirect("student:profile")
        else:
            student = StudentDetails.objects.get(user=user)
            student.name = name
            student.email = email
            student.phone = ph_no
            student.address = address
            student.date_of_birth = dob
            student.blood_group = blood_group
            student.course = course
            student.gender = gender
            student.branch = branch
            student.year = year
            student.sem = semester
            student.roll_no = roll_no
            student.reg_no = reg_no
            if resume:
                if student.resume:
                    student.resume.delete()
                student.resume = resume
            student.cgpa = cgpa
            student.job_title = job_title
            student.company_name = company_name
            student.company_location = company_location
            student.salary = salary
            if img:
                if student.profile_picture:
                    student.profile_picture.delete()
                student.profile_picture = img
            if student.is_resume_approved == None:
                student.is_resume_approved = False
            student.save()
    blood_groups = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
    semesters = [str(i) for i in range(1, 7)]
    years = ['1', '2', '3']
    degree = {}
    for i in DegreeSpecialization.objects.values("degree").distinct():
        specialization = []
        for j in DegreeSpecialization.objects.filter(degree=i["degree"]):
            specialization.append(j.specialization)
        degree[i["degree"]] = specialization
    content = {
        "user_data" : UserPermission.objects.get(user=request.user),
        "student":StudentDetails.objects.filter(user=request.user).first(),
        'blood_groups': blood_groups,
        'semesters': semesters,
        'years': years,
        'degrees': json.dumps(degree),
        "degrees_list":degree,
        "notifications" : Notification.objects.filter(user=request.user).order_by("-id"),
        "notifications_count" : Notification.objects.filter(user=request.user,is_read=False).count()
    }
    return render(request,"student/profile.html",content)


def training(request):
    content = {
        "user_data" : UserPermission.objects.get(user=request.user),
        "trainings" : Training.objects.all(),
        "notifications" : Notification.objects.filter(user=request.user).order_by("-id"),
        "notifications_count" : Notification.objects.filter(user=request.user,is_read=False).count()
    }
    return render(request,"student/training.html",content)


def mark_notification_read(request, pk):
    try:
        print(pk)
        notif = Notification.objects.get(pk=pk, user=request.user)
        notif.is_read = True
        notif.save()
        print("chsng")

        # Return a minimal replacement (same structure but marked as read)
        response = HttpResponse(
            f'<a class="dropdown-item d-flex py-3 border-bottom notification-item" '
            f'style="white-space: normal;" data-id="{notif.id}">'
            f'<div class="w-100">'
            f'<p class="mb-0 text-muted small text-wrap">{notif.message}</p>'
            f'</div></a>'
        )
        # Fire an event so the badge count can be updated client-side
        return trigger_client_event(response, "notificationRead", {"id": pk})
    except Notification.DoesNotExist:
        return HttpResponse(status=404)
