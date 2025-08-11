from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q

from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from .models import UserPermission,Principal,Notification,DegreeSpecialization
from student.models import StudentDetails
from company.models import JobDetails,CompanyDetails
from teacher.models import TeacherDetails

def add_notifications(request):
    user = request.user

    # Check for pending approvals
    re_company = UserPermission.objects.filter(is_company=True, is_approved=False)
    re_teacher = UserPermission.objects.filter(is_teacher=True, is_approved=False)
    re_student = UserPermission.objects.filter(is_student=True, is_approved=False)

    # Collect all current notification messages for this user
    active_notifications = []

    # Company notification
    if re_company.exists():
        msg = f"There are {re_company.count()} company accounts awaiting approval."
        Notification.objects.update_or_create(
            user=user,
            message=msg,
            defaults={"is_read": False}
        )
        active_notifications.append(msg)

    # Teacher notification
    if re_teacher.exists():
        msg = f"There are {re_teacher.count()} teacher accounts awaiting approval."
        Notification.objects.update_or_create(
            user=user,
            message=msg,
            defaults={"is_read": False}
        )
        active_notifications.append(msg)

    # Student notification
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
def index(request):
    return render(request,"unauthpages/index.html")

def userlogin(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(username=username,password=password)
        if user is not None:
            user_permission = UserPermission.objects.get(user__username= username)
            login(request,user)
            if user_permission.is_approved:
                messages.success(request,"Login Successful")
                if user_permission.is_student:
                    return redirect("student:student")
                if user_permission.is_company:
                    return redirect("company:company")
                if user_permission.is_teacher:
                    return redirect("teacher:teacher")
                if user_permission.is_principal:
                    return redirect("app:dashboard")
            else:
                if user_permission.is_student:
                    messages.info(request,"Wait for the teacher to approve your request")
                else:
                    messages.info(request,"Wait for the admin to approve your request")
                
                return redirect("app:login")
        elif User.objects.filter(username=username).exists():
            messages.error(request,"Incorrect password")
            return redirect("app:login")
        else:
            messages.error(request,"No user registered in this name")
            return redirect("app:login")
    return render(request,"unauthpages/login.html")

def userregister(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password1")
        cpassword = request.POST.get("password2")
        user_type = request.POST.get("user_type")
        if password != cpassword:
            messages.error(request,"Password didn't match")
            return redirect("app:register")
        if User.objects.filter(username=username).exists():
            messages.error(request,"User Name is already taken")
            return redirect("app:register")
        if user_type == "student":
            degree_program = request.POST.get("degree_program")
            branch = request.POST.get("branch")
            user = User.objects.create_user(username=username,password=password)
            user.save()
            StudentDetails.objects.create(user=user,name=username,course=degree_program,branch=branch).save()
            
            UserPermission(user=user,is_student=True).save()
            messages.success(request,"Your registered Successfully")
            return redirect("app:login")
        elif user_type == "teacher":
            user = User.objects.create_user(username=username,password=password)
            user.save()
            department = request.POST.get("department")
            TeacherDetails.objects.create(user=user,name=username,department=department).save()
            UserPermission(user=user,is_teacher=True).save()
            messages.success(request,"Your registered Successfully")
            return redirect("app:home")
        elif user_type == "company":
            user = User.objects.create_user(username=username,password=password)
            user.save()
            UserPermission(user=user,is_company=True).save()
            return redirect("app:home")
        
    return render(request,"unauthpages/register.html")

def userlogout(request):
    logout(request)
    return redirect("app:home")

@login_required(login_url="app:login")
def dashboard(request):
    
    print(DegreeSpecialization.objects.all())
    content = {
        "user_data": UserPermission.objects.get(user=request.user),
        "notifications": add_notifications(request),
        "degree_specializations": DegreeSpecialization.objects.all(),
        "teacher_count": UserPermission.objects.filter(is_teacher=True).count(),
        "student_count": UserPermission.objects.filter(is_student=True).count(),
        "degree_count": DegreeSpecialization.objects.values("degree").distinct().count(),
        "specialization_count": DegreeSpecialization.objects.all().count(),
    }

    
    return render(request, "app/dashboard.html", content)


@login_required(login_url="app:login")
def profile(request):
    if request.method == "POST":
        try:
            img = request.FILES["profile_picture"]
        except:
            img = None
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        address = request.POST.get("address")
        hide = request.POST.get("hide")
        print(img)
        print(hide)
        if hide == "edit":
            user = request.user
            user.email = email
            user.save()
            principal = Principal.objects.get(user=user)
            principal.name = name
            principal.email = email
            principal.phone = phone
            principal.address = address
            if img:
                if principal.profile_picture:
                    principal.profile_picture.delete()
                principal.profile_picture = img
            
            principal.save()
            messages.success(request,"Your profile has been updated")
            return redirect("app:profile")
        else:
            user = request.user
            user.email = email
            user.save()
            Principal.objects.create(user=user,name=name,email=email,phone=phone,address=address,profile_picture=img).save()
            messages.success(request,"Your profile has been updated")
            return redirect("app:profile")
    content = {
        "principal":Principal.objects.filter(user=request.user).first(),
        "user_data" : UserPermission.objects.get(user=request.user),
        "notifications": add_notifications(request)
    }
    return render(request,"app/Profile.html",content)

@login_required(login_url="app:login")
def approve(request):
    if request.method == "POST":
        username = request.POST.get("username")
        action = request.POST.get("action")
        print(action)
        if action == "delete":
            user = User.objects.get(username=username)
            user.delete()
            messages.success(request,"User has been rejected")
            return redirect("app:approve")
        elif action == "approve":
            user = User.objects.get(username=username)
            user_permission = UserPermission.objects.get(user=user)
            user_permission.is_approved = True
            user_permission.save()
            messages.success(request,"User has been approved")
            return redirect("app:approve")
    content = {
        "teacher":UserPermission.objects.filter(is_teacher=True,is_approved=False),
        "company":UserPermission.objects.filter(is_company=True,is_approved=False),
        "user_data" : UserPermission.objects.get(user=request.user),
        "notifications": add_notifications(request)

    }
    return render(request,"app/approve.html",content)


@login_required(login_url="app:login")
def allStudents(request):
    students = StudentDetails.objects.filter(
    user__user_permission__is_student=True,
    user__user_permission__is_approved=True
)
    content = {
        "students":students,
        "user_data" : UserPermission.objects.get(user=request.user),
        "notifications": add_notifications(request)
    }
    return render(request,"app/students.html",content)


def teacher(request):
    if request.method == "POST":
        id = request.POST.get("teacher_id")
        designation = request.POST.get("designation")
        department = request.POST.get("department")
        specialization = request.POST.get("specialization")
        is_hod = request.POST.get("is_hod") == "on"
        placement_faculty = request.POST.get("is_placement") == "on"
        print(placement_faculty)
        teacher = TeacherDetails.objects.get(id=id)
        teacher.specialization = specialization
        teacher.designation = designation
        teacher.department = department
        teacher.is_hod = is_hod
        teacher.is_placement_faculty = placement_faculty
        teacher.save()
        print(designation,id,department,is_hod,placement_faculty)
        messages.success(request,"Your profile has been updated")
        return redirect("app:teacher")

    print(DegreeSpecialization.objects.values("degree").distinct()[0])
    
    content = {
        "user_data" : UserPermission.objects.get(user=request.user),
        "teachers":TeacherDetails.objects.filter(user__user_permission__is_teacher=True,user__user_permission__is_approved=True),
        "notifications": add_notifications(request),
        "degrees":DegreeSpecialization.objects.values("degree").distinct(),
        "specializations":DegreeSpecialization.objects.all()
    }

    print(content["teachers"])

    return render(request,"app/teacher.html",content)


def company(request):
    content = {
        "user_data" : UserPermission.objects.get(user=request.user),
        "companies":CompanyDetails.objects.filter(user__user_permission__is_company=True,user__user_permission__is_approved=True),
        "notifications": add_notifications(request)
    }
    return render(request,"app/company.html",content)

def add_degree_specialization(request):
    if request.method == "POST":
        degree = request.POST.get("degree_name")
        specialization = request.POST.get("specialization_name")
        id = request.POST.get("id")
        if id:
            degree_specialization = DegreeSpecialization.objects.get(id=id)
            degree_specialization.degree = degree
            degree_specialization.specialization = specialization
            degree_specialization.save()
            messages.success(request,"Your degree specialization has been updated")
            return redirect("app:dashboard")
        DegreeSpecialization.objects.create(user=request.user,degree=degree,specialization=specialization).save()
        messages.success(request,"Your degree specialization has been added")
        return redirect("app:dashboard")
    return redirect("app:dashboard")



def delete_degree_specialization(request,id):
    degree_specialization = DegreeSpecialization.objects.get(id=id)
    degree_specialization.delete()
    messages.success(request,"Your degree specialization has been deleted")
    return redirect("app:dashboard")
