from django.shortcuts import render,redirect
from django.contrib import messages
from app.models import UserPermission,Notification
from .models import TeacherDetails
from student.models import StudentDetails

def add_notifications(request):
    user = request.user

    # Check for pending approvals
    re_student = UserPermission.objects.filter(is_student=True, is_approved=False)

    # Collect all current notification messages for this user
    active_notifications = []

    # Company notification
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
        "user_data":UserPermission.objects.get(user=request.user)
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
    departments = ['Computer Science', 'Mechanical', 'Electrical', 'Civil', 'Electronics']
    designations = ['Assistant Professor', 'Associate Professor', 'Professor', 'Lecturer']
    try:
        teacher = TeacherDetails.objects.get(user=request.user)
    except:
        teacher = None
    content = {
        "user_data":UserPermission.objects.get(user=request.user),
        'blood_groups': blood_groups,
        'genders': genders,
        'departments': departments,
        'designations': designations,
        'teacher':teacher,
    }
    return render(request,"teacher/profile.html",content)

def approvestudents(request):
    teacher = TeacherDetails.objects.get(user=request.user)
    students = StudentDetails.objects.filter(user__user_permission__is_student=True,user__user_permission__is_approved=False,branch=teacher.department)

    content = {
        "user_data":UserPermission.objects.get(user=request.user),
        "students":students,
        "notifications":add_notifications(request),
    }
    return render(request,"teacher/approvestudents.html",content)

