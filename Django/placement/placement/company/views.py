from django.shortcuts import render,redirect
from app.models import UserPermission
from .models import CompanyDetails
from django.contrib import messages

# Create your views here.
def dashboard(request):
    context = {
        "user_data" : UserPermission.objects.get(user=request.user),
    }
    return render(request,"company/dashboard.html",context)

def profile(request):
    if request.method == "POST":
        try:
            img = request.FILES.get("profile_pictures")
        except:
            img = None
        c_name= request.POST.get("name")
        industry_type = request.POST.get("industry_type")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        location = request.POST.get("location")
        is_edit =  request.POST.get("hide")
        
        if is_edit is None:
            CompanyDetails(user=request.user,name=c_name,email= email,phone=phone,location=location,industry_type=industry_type,profile_picture=img).save()
            messages.success(request,"Profile updated successfully")
            return redirect("company:profile")
        else:
            pass

    context = {
        "user_data" : UserPermission.objects.get(user=request.user),
        "company" : CompanyDetails.objects.filter(user=request.user).first(),
    }
    return render(request,"company/Profile.html",context)