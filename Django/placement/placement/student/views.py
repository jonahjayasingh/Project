from django.shortcuts import render,redirect
from app.models import UserPermission
from .models import StudentDetails
from django.contrib.auth.models import User
from django.contrib import messages

# Create your views here.
def dashboard(request):
    content = {
        "user_data" : UserPermission.objects.get(user=request.user)
    }
    print(content)
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
        user = User.objects.get(username=request.user)
        if is_edit is None:
            StudentDetails(user=user,name=name,email=email,phone=ph_no,address=address,date_of_birth=dob,gender=gender,blood_group=blood_group,profile_picture=img,course=course,branch=branch,year=year,sem= semester,roll_no=roll_no,reg_no=reg_no,cgpa=cgpa).save()
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
            student.branch = branch
            student.year = year
            student.sem = semester
            student.roll_no = roll_no
            student.reg_no = reg_no
            student.cgpa = cgpa
            if img:
                if student.profile_picture:
                    student.profile_picture.delete()
                student.profile_picture = img
            student.save()
    blood_groups = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
    semesters = [str(i) for i in range(1, 9)]
    years = ['1', '2', '3', '4']
    content = {
        "user_data" : UserPermission.objects.get(user=request.user),
        "student":StudentDetails.objects.filter(user=request.user).first(),
        'blood_groups': blood_groups,
        'semesters': semesters,
        'years': years,
    }
    print(content)
    return render(request,"student/profile.html",content)