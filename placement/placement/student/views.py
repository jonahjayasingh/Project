from django.shortcuts import render
from app.models import UserPermission
from .models import StudentDetails

# Create your views here.
def dashboard(request):
    content = {
        "user_data" : UserPermission.objects.get(user=request.user)
    }
    print(content)
    return render(request,"student/dashboard.html",content)

def profile(request):
    content = {
        "user_data" : UserPermission.objects.get(user=request.user),
        "student":StudentDetails.objects.filter(user=request.user).first()
    }
    print(content)
    return render(request,"student/profile.html",content)