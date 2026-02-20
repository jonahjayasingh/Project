from django.db.models import Q
from django.http import HttpResponse
from django.utils import timezone
from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import User
from openpyxl import Workbook
from Coordinator.models import Events,Gallery,Mcq,Question ,Profile,Certificate,Notification,EventRegister
from django.db.models import Max

# Create your views here.
def index(request):
    coordinator = User.objects.filter(is_superuser=True,is_staff=True).exclude(username="admin")
    
    content = {
        "notifications":Notification.objects.all().order_by("-id")[:5],
        "events":Events.objects.all().order_by("-event_date")[:10],
        "coordinators":coordinator,
        "galleries":Gallery.objects.filter(id__in=Gallery.objects.values('gallery_type').annotate(last_id=Max('id')).values('last_id'))

    }
    return render(request,"unauth/index.html",content)

def verify_certificate(request,certificate_id):
    certificate = Certificate.objects.get(cert_id=certificate_id)
    if certificate:
        return render(request,"unauth/verify_certificate.html",{"certificate":certificate})
    else:
        messages.error(request,"Certificate not found")
        return redirect("coordinator:index")



def userlogin(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request,username=username,password=password)
        if user is not None:
            
            if user.is_superuser :
                if Profile.objects.filter(user=user).exists():
                    pass
                else:
                    Profile.objects.create(user=user)
                login(request,user)
                messages.success(request,"You are logged in")
                return redirect("coordinator:dashboard")
            elif user.is_staff:
                profile = Profile.objects.filter(user=user).first()
        
                if profile.type == "student" and profile.user.is_staff:
                    if Profile.objects.filter(user=user).exists():
                        login(request,user)
                        messages.success(request,"You are logged in")
                        return redirect("student:student")
                    else:
                        Profile.objects.create(user=user)
                        login(request,user)
                        messages.success(request,"You are logged in")
                        return redirect("student:student")
                else:
                    if Profile.objects.filter(user=user).exists()  :
                        login(request,user)
                        messages.success(request,"You are logged in")
                        return redirect("coordinator:dashboard")
                    else:
                        Profile.objects.create(user=user)
                        login(request,user)
                        messages.success(request,"You are logged in")
                        return redirect("coordinator:dashboard")
            else:
                messages.error(request,"wait for admin approval")
                return redirect("coordinator:userlogin")
        else:
            if User.objects.filter(username=username).exists():
                messages.error(request,"Password is incorrect")
                return redirect("coordinator:userlogin")
            else:
                messages.error(request,"Username does not exist")
                return redirect("coordinator:userlogin")
    return render(request,"unauth/login.html")

def userregister(request):
    if request.method == "POST":
        type = request.POST.get("user_type")
        name = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirmPassword = request.POST.get("confirm_password")
        admission_no = request.POST.get("admission_no")
        registration_no = request.POST.get("registration_no")
        branch = request.POST.get("branch")
        year = request.POST.get("year")
        dob = request.POST.get("date_of_birth")
        address = request.POST.get("address")
        profile_pic = request.FILES.get("profile_picture")
        phone_number = request.POST.get("phone_number")

        if password != confirmPassword:
            messages.error(request,"Password does not match")
            return redirect("coordinator:userregister")
        elif User.objects.filter(username=email).exists():
            messages.error(request,"Email already exists")
            return redirect("coordinator:userregister")
        else:
            if User.objects.filter(username=name).exists():
                messages.error(request,"Username already taken")
                return redirect("coordinator:userregister")
            else:
                user = User.objects.create_user(username=name,email=email,password=password)
                user.save()
                if type == "student":
                    Profile.objects.create(user=user,type=type,address=address,admission_no=admission_no,registration_no=registration_no,branch=branch,year=year,dob=dob,profile_pic=profile_pic,phone=phone_number)
                else:
                    Profile.objects.create(user=user,type=type,address=address,profile_pic=profile_pic,phone=phone_number)
                messages.success(request,"Account created successfully")
                return redirect("coordinator:userlogin")
    return render(request,"unauth/register.html")

def userlogout(request):
    logout(request)
    return redirect("coordinator:index")

def change_password(request):
    if request.method == "POST":
        old_password = request.POST.get("old_password")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")
        if new_password != confirm_password:
            messages.error(request,"Password does not match")
            return redirect("coordinator:change_password")
        elif old_password == new_password:
            messages.error(request,"New password cannot be same as old password")
            return redirect("coordinator:change_password")
        elif len(new_password) < 8:
            messages.error(request,"Password must be at least 8 characters long")
            return redirect("coordinator:change_password")
        else:
            user = request.user
            if user.check_password(old_password):
                user.set_password(new_password)
                user.save()
                logout(request)
                messages.success(request,"Password changed successfully")
                return redirect("coordinator:userlogin")
            else:
                messages.error(request,"Old password is incorrect")
                return redirect("coordinator:change_password")
    return render(request,"unauth/change_password.html")

def dashboard(request):
    
    if request.method == "POST":
        event_name = request.POST.get("event_name")
        event_date = request.POST.get("event_date")
        event_description = request.POST.get("event_description")
        event_mcq = request.POST.get("event_mcq")
        event_type = request.POST.get("event_type")
        
        event_location = request.POST.get("event_location")
        event_image = request.FILES.get("event_image")
        edit_event_id = request.POST.get("edit_event_id")
        if edit_event_id:
            event = Events.objects.get(id=edit_event_id)
            event.event_name = event_name
            event.event_date = event_date
            event.event_description = event_description
            event.event_location = event_location
            event.event_type = event_type
            if event_image:
                event.event_image.delete()
                event.event_image = event_image
            if event_mcq:
                event_mcq = Mcq.objects.get(id=event_mcq)
                event.event_mcq = event_mcq
            event.save()
            messages.success(request,"Event updated successfully")
            return redirect("coordinator:dashboard")
        event = Events.objects.create(user=request.user,event_name=event_name,event_date=event_date,event_type=event_type,event_description=event_description,event_location=event_location,event_image=event_image)
        event.save()
        messages.success(request,"Image uploaded successfully")
        return redirect("coordinator:dashboard")
    content = {
        "events":Events.objects.all().order_by("-event_date"),
        "gallery":Gallery.objects.all().order_by("-id"),
        "MCQ":Mcq.objects.all().order_by("-id")
    }
    return render(request,"Coordinator/dashboard.html",content)

def notification(request):
    if request.POST:
        message = request.POST.get("message")
        op = request.POST.get("op")
        event = request.POST.get("event")
        
        if op == "edit":
            event = Events.objects.get(id=event)
            notification_id = request.POST.get("notification_id")
            notification = Notification.objects.get(id=notification_id)
            notification.event = event
            notification.message = message
            notification.save()
            messages.success(request,"Notification updated successfully")
            return redirect("coordinator:notification")
        elif op == "delete":
            notification_id = request.POST.get("notification_id")
            notification = Notification.objects.get(id=notification_id)
            notification.delete()
            messages.success(request,"Notification deleted successfully")   
            return redirect("coordinator:notification")
        else:
            event = Events.objects.get(id=event)
            Notification.objects.create(user=request.user,message=message,event=event)
            messages.success(request,"Notification sent successfully")
            return redirect("coordinator:notification")
        pass
    now = timezone.now()
    all_events = Events.objects.all().filter(event_date__gte=now).order_by("-id")
    notifications = Notification.objects.all().order_by("-id")
    return render(request, "Coordinator/notification.html", {"all_events": all_events,"notifications":notifications})


def delete_event(request):
    if request.method == "POST":
        event_id = request.POST.get("delete_event_id")
        event = Events.objects.get(id=event_id)
        if event.event_image:
            event.event_image.delete()
        event.delete()
        messages.success(request,"Event deleted successfully")
        return redirect("coordinator:dashboard")
    return redirect("coordinator:dashboard")

def add_gallery(request):
    if request.method == "POST":
        image = request.FILES.get("image")
        caption = request.POST.get("caption")
        gallery_type = request.POST.get("gallery_type")
        edit_gallery_id = request.POST.get("edit_gallery_id")
        if edit_gallery_id:
            gallery = Gallery.objects.get(id=edit_gallery_id)
            gallery.user = request.user
            if image != None:
                gallery.image.delete()
                gallery.image = image
            gallery.caption = caption
            gallery.gallery_type = gallery_type
            gallery.save()
            messages.success(request,"Image updated successfully")
            return redirect("coordinator:dashboard")
        Gallery.objects.create(user=request.user,image=image,caption=caption,gallery_type=gallery_type)
        messages.success(request,"Image uploaded successfully")
        return redirect("coordinator:dashboard")


def delete_gallery(request):
    if request.method == "POST":
        gallery_id = request.POST.get("delete_gallery_id")
        gallery = Gallery.objects.get(id=gallery_id)
        if gallery.image:
            gallery.image.delete()
        gallery.delete()
        messages.success(request,"Gallery deleted successfully")
        return redirect("coordinator:dashboard")
    return redirect("coordinator:dashboard")

def gallery(request):
    content = {
        "galleries":Gallery.objects.all().order_by("-id"),
        "types":Gallery.objects.values_list("gallery_type",flat=True).distinct(),
        "notifications":Notification.objects.all().order_by("-id")
    }
    return render(request,"unauth/gallery.html",content)

def event(request):
    content = {
        "events":Events.objects.all().order_by("-event_date"),
        "notifications":Notification.objects.all().order_by("-id")
    }
    return render(request,"unauth/event.html",content)


def profile(request):
    if request.method == "POST":
        phone = request.POST.get("phone")
        address = request.POST.get("address")
        profile_pic = request.FILES.get("avatar")
        
        email = request.POST.get("email") 
        user = User.objects.get(username=request.user.username)
        user.email = email
        user.save()
        profile = Profile.objects.get(user=request.user)
        profile.phone = phone
        profile.address = address        
        if profile_pic:
            if profile.profile_pic:
                profile.profile_pic.delete()
            profile.profile_pic = profile_pic
        
        profile.save()
        messages.success(request,"Profile updated successfully")
        return redirect("coordinator:profile")
    return render(request,"Coordinator/profile.html",{
        "profile":Profile.objects.get(user=request.user)
    })


def approve_students(request):
    if request.method == "POST":
        student_id = request.POST.get("student_id")
        student = User.objects.get(id=student_id)
        action = request.POST.get("action")
        if action == "reject":
            student.delete()
            messages.success(request,"Student successfully removed" )
            return redirect("coordinator:approve_students")
        student.is_staff= True
        student.save()
        messages.success(request,"Student approved successfully")
        return redirect("coordinator:approve_students")
    content = {
        "students":User.objects.filter(is_superuser=False),
        "astudents": len(User.objects.filter(is_staff=True,is_superuser=False)),
        "pstudents":len(User.objects.filter(is_staff=False,is_superuser=False)),
    }
    return render(request,"Coordinator/approve_student.html",content)   


def mcq(request):
    content = {
        "quizzes":Mcq.objects.all().order_by("-id")
    }
    return render(request,"Coordinator/mcq.html",content)
import json
def create_mcq(request):
    if request.method == "POST":
        data = json.loads(request.body)
        mcq  = Mcq.objects.create(user=User.objects.get(username="admin"),mcq_title=data['formName'],no_of_questions=data['questionCount'],mcq_duration=data['mcqDuration'],date=data['mcqDate'],is_active=True)
        print(data)
        for q in data['questions']:
            
            Question.objects.create(
                mcq=mcq,
                question=q['text'],
                option1=q['options'][0]['text'],
                option2=q['options'][1]['text'],
                option3=q['options'][2]['text'],
                option4=q['options'][3]['text'],
                answer=q['correctAnswer']
            )
        return redirect("coordinator:mcq")
    return render(request,"Coordinator/form.html")

from django.shortcuts import get_object_or_404
def edit_mcq(request, mcq_id):
    mcq = get_object_or_404(Mcq, id=mcq_id)
    questions = mcq.questions.all()

    if request.method == "POST":

        # Handle questions
        question_ids = request.POST.getlist("question_ids")  # 
                # Update MCQ title
        mcq.mcq_title = request.POST.get("mcq_title")
        # Update MCQ duration
        mcq.mcq_duration = request.POST.get("mcq_duration")
        # Update MCQ date
        mcq.date = request.POST.get("mcq_date")
        # Update MCQ questions
        mcq.no_of_questions = len(question_ids) 
        mcq.save()

        for q_id in question_ids:
            question = get_object_or_404(Question, id=q_id, mcq=mcq)

            # Update question text
            question_text = request.POST.get(f"question_text_{q_id}")
            question.question = question_text

            # Update options
            question.option1 = request.POST.get("option1", "")
            question.option2 = request.POST.get("option2", "")
            question.option3 = request.POST.get("option3", "")
            question.option4 = request.POST.get("option4", "")

            # Update correct answer
            correct_answer = request.POST.get(f"correct_answer_{q_id}")
            question.answer = correct_answer

            question.save()

        messages.success(request, "MCQ updated successfully!")
        return redirect("coordinator:mcq")

    return render(request, "Coordinator/edit_form.html", {"mcq": mcq, "questions": questions})

def delete_mcq(request, mcq_id):
    mcq = get_object_or_404(Mcq, id=mcq_id)
    mcq.delete()
    messages.success(request, "MCQ deleted successfully!")
    return redirect("coordinator:mcq")


def toggle_mcq_status(request, mcq_id):
    mcq = get_object_or_404(Mcq, id=mcq_id)
    mcq.is_active = not mcq.is_active
    mcq.save()
    messages.success(request, "MCQ status updated successfully!")
    return redirect("coordinator:mcq")


def export_event_participants(request, event_id):
    event = get_object_or_404(Events, id=event_id)
    event_registers = EventRegister.objects.filter(event=event)

    # Create response for Excel file
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = f'attachment; filename="{event.event_name}_participants.xlsx"'

    # Create workbook and sheet
    wb = Workbook()
    ws = wb.active
    ws.title = event.event_name

    if event.event_type == "Exhibition":
        headers = ["Name", "Email", "Registration date", "Project Title", "Project Description", "Branch"]
        ws.append(headers)

        for reg in event_registers:
            ws.append([
                reg.user.username,
                reg.user.email,
                reg.date.strftime("%Y-%m-%d"),
                reg.project_title,
                reg.project_description,
                reg.branch,
            ])
    else:
        headers = ["Name", "Email", "Registration date", "Branch"]
        ws.append(headers)

        for reg in event_registers:
            ws.append([
                reg.user.username,
                reg.user.email,
                reg.date.strftime("%Y-%m-%d"),
                reg.branch,
            ])

    # Save the workbook to the response
    wb.save(response)
    return response
