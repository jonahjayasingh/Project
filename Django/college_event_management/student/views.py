from django.shortcuts import render,redirect
from Coordinator.models import Mcq,Events,EventRegister,Certificate,Profile,StudentSGPA ,Subject
import json
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib import messages
from django.db.models import Q
import uuid
from .certificate import generate_certificate_passed_pdf,generate_certificate_attended_pdf
# Create your views here.

def index(request):
    today = timezone.now()
    today = today.date() 
    events = Events.objects.filter(event_registers__user=request.user,event_date__gte=today).order_by("event_date").exclude(certificates__user=request.user)
    print(events)
    content = {
        "now": timezone.now(),
        "events": Events.objects.filter(
                Q(event_mcq__isnull=False) | Q(event_type__isnull=False),  # OR condition
                event_date__gte=today                                       # AND with event_date >= today
            ).exclude(
                event_registers__user=request.user
            ).order_by("event_date"),
        "registered_events": Events.objects.filter(event_registers__user=request.user,event_date__gte=today).order_by("event_date").exclude(certificates__user=request.user),
        "today": today

    }
    
    return render(request, "student/dashboard.html", content)


def student_register(request):
    if request.method == "POST":
        event_id = request.POST.get("event_id")
        event = Events.objects.get(id=event_id)
        if event.event_type == "Exibition":
            project_name = request.POST.get("project_title")
            project_description = request.POST.get("project_description")
            project_members = request.POST.get("project_members")
            branch = request.POST.get("branch")
            count = 0
            for i in project_members.split(","):
                if User.objects.filter(username=i).exists():
                    count+=1
            if count != len(project_members.split(",")):
                messages.error(request, "One or more project members do not exist.")
                return redirect("student:student")
            for i in project_members.split(","):
                EventRegister.objects.create(
                    user=User.objects.get(username=i),
                    event=event,
                    project_title=project_name,
                    project_description=project_description,
                    branch=branch
                )
        else:
            branch = request.POST.get("branch")
            user = request.user
            EventRegister.objects.create(
                user=user,
                event=event,
                branch=branch
            )
        return redirect("student:student")

def cancel_register(request):
    if request.method == "POST":
        cancel_event_id = request.POST.get("cancel_event_id")
        if EventRegister.objects.filter(event_id = cancel_event_id).exists():
            EventRegister.objects.get(event_id = cancel_event_id).delete()
        
        return redirect("student:student")
    

def mcq_exam(request,id):
    event = Events.objects.get(id=id)
    mcq = Mcq.objects.get(id=event.event_mcq.id)
    if request.method == "POST":
        name = request.POST.get("event_name")
        print(name)
        event = Events.objects.get(event_name = name)
        question = Mcq.objects.get(id=event.event_mcq.id)
        print(request.POST)
        mark = 0
        for i in request.POST:
            print(question.questions.all())
            if question.questions.all().filter(question=i).exists():
                ques = question.questions.all().get(question=i)
                correct_option = getattr(ques, f"option{ques.answer}")
                
                if correct_option == request.POST.get(f"{i}"):
                    mark+=1
        cert_id = str(uuid.uuid4())[:12].upper()
        print(cert_id)
        if mark == len(question.questions.all()):
            pdf_path = generate_certificate_passed_pdf(request.user.username, event.event_name,cert_id)
            Certificate.objects.create(
                user=request.user,
                event=event,
                cert_id=cert_id,
                passed=True,
                pdf = pdf_path
            )
        else:
            pdf_path = generate_certificate_attended_pdf(request.user.username, event.event_name,cert_id)
            Certificate.objects.create(
                user=request.user,
                event=mcq.mcq_events.first(),
                cert_id=cert_id,
                passed=False,
                pdf = pdf_path
            )
        return redirect("student:student")
    questions = []
    for question in mcq.questions.all():
        questions.append({
            'text': question.question,
            'options': question.get_options()
        })
    # print(questions)
    mcq_data = {
        "mcq_id": mcq.id,
        "mcq_title": mcq.mcq_title,
        "mcq_duration": mcq.mcq_duration,
        "mcq_questions": questions
        ,"event_name": event.event_name
    }
    
    context = {
        "mcq": mcq_data,
        "total_questions": len(questions)
    }
    return render(request, "student/mcq_exam.html", context)

def profile(request):
    if request.method == "POST":
        print(request.POST.get("email"))
        user = User.objects.get(username=request.user.username)
        user.email = request.POST.get("email")
        user.save()
        profile = Profile.objects.get(user=request.user)
        if request.FILES.get("avatar"): 
            profile.profile_pic = request.FILES.get("avatar")
        profile.phone = request.POST.get("phone")
        profile.address = request.POST.get("address")
        profile.dob = request.POST.get("dob")
        profile.branch = request.POST.get("branch")
        profile.year = request.POST.get("year")
        profile.admission_no = request.POST.get("admission_no")
        profile.registration_no = request.POST.get("registration_no")
        profile.father_name = request.POST.get("father_name")
        profile.mother_name = request.POST.get("mother_name")
        profile.ten_th = request.POST.get("ten_th")
        profile.twelve_th = request.POST.get("twelve_th")
        

        profile.save()
        messages.success(request, "Profile updated successfully.")
        return redirect("student:profile")
    return render(request, "student/profile.html",{"profile":Profile.objects.get(user=request.user),"sgpa":StudentSGPA.objects.filter(student=request.user.profile)})

def my_certificates(request):
    return render(request, "student/my_certificates.html",{"certificates":Certificate.objects.filter(user=request.user)})
from student.course_data import data

def handle_sgpa(request):
    if request.method == "POST":
        print(request.POST)
        semester = request.POST.get("semester")
        subjects = data[f"semester_{semester}"]
       
        if StudentSGPA.objects.filter(student=request.user.profile, semester=semester).exists():
            subject_obj = StudentSGPA.objects.get(student=request.user.profile, semester=semester)
            subjects = subject_obj.subjects.filter(subject_code__in=subjects.keys())
            for subject in subjects:
                subject.subject_grade = request.POST.get(f"course_grades[{subject.subject_code}]")
                subject.subject_credits = float(request.POST.get(f"course_credits[{subject.subject_code}]"))
                subject.save()
            return redirect("student:profile")
        else:
            subject_obj = StudentSGPA.objects.create(
                student=request.user.profile,
                semester=semester,
            )
        print(semester)
        
        for subject in subjects:
            subject_data = subjects[subject]
            subject_name = subject_data["course"]
            subject_grade = request.POST.get(f"course_grades[{subject}]")
            subject_credit = request.POST.get(f"course_credits[{subject}]")
            Subject.objects.create(
                student_sgpa=subject_obj,
                subject_name=subject_name,
                subject_code=subject,
                subject_grade=subject_grade,
                subject_credits=float(subject_credit)
            )
        messages.success(request, "SGPA updated successfully.")
        return redirect("student:profile") 
    return redirect("student:profile")
