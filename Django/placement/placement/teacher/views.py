from django.shortcuts import render,redirect
from django.contrib import messages
from app.models import UserPermission,Notification,DegreeSpecialization
from .models import TeacherDetails, Training
from student.models import StudentDetails
import json
from django.contrib.auth.models import User

def add_notifications(request):
    user = request.user
    teacher = TeacherDetails.objects.get(user=request.user)

    # Check for pending approvals
    re_student = StudentDetails.objects.filter(user__user_permission__is_approved=False,user__user_permission__is_student=True,branch=teacher.specialization,course=teacher.department)
    
    
    active_notifications = []
    print(re_student[0])
    msg = f"There are {re_student.count()} student accounts awaiting approval."
    if Notification.objects.filter(user=user,message__icontains=msg).exists():
        notifications = Notification.objects.filter(user=user).order_by("-date")
        return notifications
    if re_student.exists():
        msg = f"There are {re_student.count()} student accounts awaiting approval."
        Notification.objects.update_or_create(
            user=user,
            message=msg,
            defaults={"is_read": False}
        )
        active_notifications.append(msg)

    # Remove outdated approval notifications (for company/teacher/student)
    Notification.objects.filter(
        user=user,
        message__icontains="accounts awaiting approval."
    ).exclude(message__in=active_notifications).delete()

    # Fetch remaining notifications for display
    notifications = Notification.objects.filter(user=user).order_by("-date")
    return notifications

# Create your views here.
def dashboard(request):
    content = {
        "user_data":UserPermission.objects.get(user=request.user),
        "notifications":add_notifications(request),
         "notifications_count" : Notification.objects.filter(user=request.user,is_read=False).count()
    }
    print(content["user_data"].is_teacher)
    
    return render(request,"teacher/dashboard.html",content)

def profile(request):
    if request.method == 'POST':
        try:
            img = request.FILES.get("profile_picture")
        except:
            img = None
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        dob = request.POST.get("date_of_birth")
        gender = request.POST.get("gender")
        blood_group = request.POST.get("blood_group")
        address = request.POST.get("address")
        hide = request.POST.get("hide")
        if hide is None:
            print(name,email,phone,dob,gender,blood_group,address,img)
            TeacherDetails.objects.create(user=request.user,name=name,email=email,phone=phone,date_of_birth=dob,gender=gender,blood_group=blood_group,address=address,profile_picture=img).save()
            messages.success(request,"Your Profile has been added")
            return redirect("teacher:profile")
        else:
            teacher = TeacherDetails.objects.get(user= request.user)
            teacher.name = name
            teacher.email = email
            teacher.phone = phone
            teacher.address = address
            teacher.gender = gender
            teacher.date_of_birth = dob
            teacher.blood_group = blood_group
            if img:
                if teacher.profile_picture:
                    teacher.profile_picture.delete()
                teacher.profile_picture = img
            teacher.save()
            messages.success(request,"Profile has been updated")
            return redirect("teacher:profile")
    
    blood_groups = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
    genders = ['Male', 'Female', 'Other']
    
    try:
        teacher = TeacherDetails.objects.get(user=request.user)
    except:
        teacher = None
    content = {
        "user_data":UserPermission.objects.get(user=request.user),
        'blood_groups': blood_groups,
        'genders': genders,
        "notifications":add_notifications(request),
        'teacher':teacher,
    }
    return render(request,"teacher/profile.html",content)

def approvestudents(request):
    teacher = TeacherDetails.objects.get(user=request.user)
    print(teacher.department)
    print(StudentDetails.objects.filter(name="S1"))
    students = StudentDetails.objects.filter(user__user_permission__is_student=True,user__user_permission__is_approved=False,course=teacher.department,branch=teacher.specialization)
    print(students)
    content = {
        "user_data":UserPermission.objects.get(user=request.user),
        "students":students,
        "notifications":add_notifications(request),
        "notifications" : Notification.objects.filter(user=request.user).order_by("-id"),
        "notifications_count" : Notification.objects.filter(user=request.user,is_read=False).count()
    }
    return render(request,"teacher/approvestudents.html",content)


def approve(request,id):
    student = StudentDetails.objects.get(id=id)
    user_permission = UserPermission.objects.get(user=student.user)
    user_permission.is_approved = True
    user_permission.save()
    messages.success(request,"Student has been approved")
    return redirect("teacher:approvestudents")

def reject(request,id):
    student = StudentDetails.objects.get(id=id)
    user = User.objects.get(id=student.user.id)
    user.delete()
    messages.success(request,"Student has been deleted")
    return redirect("teacher:approvestudents")

def resume(request):
    if request.method == "POST":
        s_id = request.POST.get("s_id")
        student = StudentDetails.object.filter(id = s_id)
        student.is_resume_approved = True
        student.save()
        Notification(user=student.user,message="Your resume has been approved").save()
        return redirect("teacher:resume")
    teacher = TeacherDetails.objects.get(user=request.user)
    students = StudentDetails.objects.filter(user__user_permission__is_student=True,user__user_permission__is_approved=True,course=teacher.department,branch=teacher.specialization, resume__isnull = False,is_resume_approved=False)
    

    content = {
        "user_data":UserPermission.objects.get(user=request.user),
        "students":students,
        "notifications":add_notifications(request),
        "notifications" : Notification.objects.filter(user=request.user).order_by("-id"),
        "notifications_count" : Notification.objects.filter(user=request.user,is_read=False).count()
    }
    return render(request,"teacher/approveresume.html",content)
    
def reject_resume(request):
    if request.method == "POST":
        s_id = request.POST.get("s_id")
        student = StudentDetails.objects.get(id = s_id)
        message = request.POST.get("feedback_message")
        student.is_resume_approved = None
        student.resume.delete()
        student.resume = None
        student.save()
        Notification(user=student.user,message=message).save()
        messages.success(request,"Resume has been rejected")
    return redirect("teacher:resume")


def all_student(request):
    if request.method == "POST":
        s_id = request.POST.get("student_id")
        message = request.POST.get("message")
        student = StudentDetails.objects.get(id=s_id)
        Notification(user=student.user,message=message).save()
        messages.success(request,f"Notification sent to {student.name} sucessfully")
        return redirect("teacher:allstudent")
    teacher = TeacherDetails.objects.get(user= request.user)
    students = StudentDetails.objects.filter(course= teacher.department,branch=teacher.specialization)
    content = {
        "user_data":UserPermission.objects.get(user=request.user),
        "students":students,
        "notifications":add_notifications(request),
        
    }
    return render(request,"teacher/allstudent.html",content)

def group_notification(request):
    if request.method == "POST":
        filter_p = request.POST.get("filter_params")
        message = request.POST.get("message")
        if filter_p:
            filter_p = json.loads(filter_p)
        print(filter_p)
        teacher = TeacherDetails.objects.get(user= request.user)
        if filter_p["search"] != "" and filter_p["year"] != "":
            students = StudentDetails.objects.filter(name__contains= filter_p["search"],year=filter_p["year"],course= teacher.department,branch=teacher.specialization)
        elif filter_p["year"] != "":
            print("year")
            students = StudentDetails.objects.filter(year=filter_p["year"],course= teacher.department,branch=teacher.specialization)
        else:
            print("search")
            students = StudentDetails.objects.filter(name__icontains= filter_p["search"],course= teacher.department,branch=teacher.specialization)
        for student in students:  
            Notification(user=student.user,message=message).save()
        messages.success(request,f"Notification sent to {len(students)} students sucessfully")
        return redirect("teacher:allstudent")
    return redirect("teacher:allstudent")

def training(request):
    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        file = request.FILES.get("file")
        training_type = request.POST.get("training_type")
        print(training_type)
        if training_type == "video":
            Training(user=request.user.teacher.first(),title=title,description=description,vedio=file).save()
        else:
            Training(user=request.user.teacher.first(),title=title,description=description,quize=file).save()
        
        messages.success(request,"Training has been added")
        return redirect("teacher:training")
    content = {
        "user_data":UserPermission.objects.get(user=request.user),
        "trainings":Training.objects.all(),
        "notifications":add_notifications(request),
        "notifications" : Notification.objects.filter(user=request.user).order_by("-id"),
        "notifications_count" : Notification.objects.filter(user=request.user,is_read=False).count()
    }
    return render(request,"teacher/training.html",content)

def delete_training(request,id):
    training = Training.objects.get(id=id)
    training.delete()
    messages.success(request,"Training has been deleted")
    return redirect("teacher:training")