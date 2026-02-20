from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .utils import predict

def home(request):
    return render(request, "home.html")

def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")
    else:
        form = UserCreationForm()
    return render(request, "news/register.html", {"form": form})

@login_required
def predict_news(request):
    result = None
    confidence = None
    text = ""
    
    if request.method == "POST":
        text = request.POST.get("news_text", "")
        if text:
            result, confidence = predict(text)
            confidence = round(confidence * 100, 2)
            
    return render(request, "news/predict.html", {
        "result": result,
        "confidence": confidence,
        "text": text
    })

