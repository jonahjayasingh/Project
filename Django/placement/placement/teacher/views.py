from django.shortcuts import render,redirect
from django.contrib import messages
from app.models import UserPermission
from .models import TeacherDetails
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
    content = {
        "user_data":UserPermission.objects.get(user=request.user),
        'blood_groups': blood_groups,
        'genders': genders,
        'departments': departments,
        'designations': designations,
        'teacher':TeacherDetails.objects.get(user=request.user)
    }
    return render(request,"teacher/profile.html",content)

def webinar(request):
    content = {
        "user_data":UserPermission.objects.get(user=request.user),
    }
    return render(request,"teacher/webinar.html",content)
