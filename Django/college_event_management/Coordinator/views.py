from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import User
from Coordinator.models import Events,Gallery,Mcq,Question 
from django.db.models import Max

# Create your views here.
def index(request):
    
    content = {
        "events":Events.objects.all()[:10],
        "galleries":Gallery.objects.filter(id__in=Gallery.objects.values('gallery_type').annotate(last_id=Max('id')).values('last_id'))

    }
    return render(request,"unauth/index.html",content)

def userlogin(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request,username=username,password=password)
        if user is not None:
            login(request,user)
            messages.success(request,"You are logged in")
            if request.user.is_superuser:
                return redirect("coordinator:dashboard")
            else:
                messages.error(request,"your not allowed to access this page")
                return redirect("student:student")
        else:
            messages.error(request,"Invalid credentials")
            return redirect("coordinator:userlogin")
    return render(request,"unauth/login.html")

def userregister(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirmPassword = request.POST.get("confirmPassword")
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
                messages.success(request,"Account created successfully")
                return redirect("coordinator:userlogin")
    return render(request,"unauth/register.html")

def userlogout(request):
    logout(request)
    messages.success(request,"You are logged out")
    return redirect("coordinator:index")

def dashboard(request):
    print(request.user.is_superuser)
    if request.method == "POST":
        event_name = request.POST.get("event_name")
        event_date = request.POST.get("event_date")
        event_description = request.POST.get("event_description")
        event_location = request.POST.get("event_location")
        event_image = request.FILES.get("event_image")
        edit_event_id = request.POST.get("edit_event_id")
        if edit_event_id:
            event = Events.objects.get(id=edit_event_id)
            event.event_name = event_name
            event.event_date = event_date
            event.event_description = event_description
            event.event_location = event_location
            if event_image:
                event.event_image.delete()
                event.event_image = event_image
            event.save()
            messages.success(request,"Event updated successfully")
            return redirect("coordinator:dashboard")
        event = Events.objects.create(user=request.user,event_name=event_name,event_date=event_date,event_description=event_description,event_location=event_location,event_image=event_image)
        event.save()
        messages.success(request,"Image uploaded successfully")
        return redirect("coordinator:dashboard")
    content = {
        "events":Events.objects.all().order_by("-id"),
        "gallery":Gallery.objects.all().order_by("-id")
    }
    return render(request,"Coordinator/dashboard.html",content)


def delete_event(request):
    if request.method == "POST":
        event_id = request.POST.get("delete_event_id")
        event = Events.objects.get(id=event_id)
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
        gallery.delete()
        messages.success(request,"Gallery deleted successfully")
        return redirect("coordinator:dashboard")
    return redirect("coordinator:dashboard")

def gallery(request):
    content = {
        "galleries":Gallery.objects.all().order_by("-id"),
        "types":Gallery.objects.values_list("gallery_type",flat=True).distinct()
    }
    return render(request,"unauth/gallery.html",content)

def event(request):
    content = {
        "events":Events.objects.all().order_by("-id")
    }
    return render(request,"unauth/event.html",content)

import json
def add_form(request):
    if request.method == "POST":
        data = json.loads(request.body)
        mcq  = Mcq.objects.create(user=User.objects.get(username="admin"),mcq_title=data['formName'],no_of_questions=data['questionCount'])
        print(data)
        for q in data['questions']:
            print(q)
            Question.objects.create(
                mcq=mcq,
                question=q['text'],
                option1=q['options'][0]['text'],
                option2=q['options'][1]['text'],
                option3=q['options'][2]['text'],
                option4=q['options'][3]['text'],
                answer=q['correctAnswer']
            )
        return redirect("coordinator:dashboard")
    return render(request,"Coordinator/form.html")


def edit_form(request):
    content = {
        "no_of_questions": 10
    }
    return render(request,"Coordinator/edit_form.html")