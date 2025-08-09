from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from .models import UserPermission,Principal
from student.models import StudentDetails
from company.models import JobDetails
from teacher.models import TeacherDetails

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
            user = User.objects.create_user(username=username,password=password)
            user.save()
            UserPermission(user=user,is_student=True,is_approved=True).save()
            messages.success(request,"Your registered Successfully")
            return redirect("app:login")
        elif user_type == "teacher":
            user = User.objects.create_user(username=username,password=password)
            user.save()
            UserPermission(user=user,is_teacher=True).save()
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
    content = {
        "user_data" : UserPermission.objects.get(user=request.user)
    }
    print(dir(content["user_data"]))
    print("check")
    print(content["user_data"].is_principal)


    return render(request,"app/dashboard.html",content)


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
        "user_data" : UserPermission.objects.get(user=request.user)

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
        "user_data" : UserPermission.objects.get(user=request.user)

    }
    return render(request,"app/approve.html",content)


@login_required(login_url="app:login")
def allStudents(request):
    students = StudentDetails.objects.filter(
    user__userpermission__is_student=True,
    user__userpermission__is_approved=True
)
    
    content = {
        "students":students,
        "user_data" : UserPermission.objects.get(user=request.user)

    }
    return render(request,"app/students.html",content)


def teacher(request):
    if request.method == "POST":
        id = request.POST.get("teacher_id")
        designation = request.POST.get("designation")
        department = request.POST.get("department")
        is_hod = request.POST.get("is_hod") == "on"
        is_placement_faculty = request.POST.get("is_placement") == "on"

        teacher = TeacherDetails.objects.get(id=id)
        teacher.designation = designation
        teacher.department = department
        teacher.is_hod = is_hod
        teacher.is_placement_faculty = is_placement_faculty
        teacher.save()
        print(designation,id,department,is_hod,is_placement_faculty)
        messages.success(request,"Your profile has been updated")
        return redirect("app:teacher")


    content = {
        "user_data" : UserPermission.objects.get(user=request.user),
        "teachers":TeacherDetails.objects.filter(user__userpermission__is_teacher=True,user__userpermission__is_approved=True)
    }
    print(content["teachers"])

    return render(request,"app/teacher.html",content)
