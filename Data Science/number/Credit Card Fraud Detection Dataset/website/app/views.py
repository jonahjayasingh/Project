from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
import joblib
import pandas as pd
import os
import json

# Path to the model and encodings
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(os.path.dirname(BASE_DIR),"website", 'model', 'credit_card.joblib')
CATEGORY_ENCODING_PATH = os.path.join(os.path.dirname(BASE_DIR), "website", 'model', 'category_encoding.json')
NAME_ENCODING_PATH = os.path.join(os.path.dirname(BASE_DIR), "website", 'model', 'name_encoding.json')

print(BASE_DIR)
# Load the model and encodings
model = None
category_mapping = {}
name_mapping = {}

if os.path.exists(MODEL_PATH):
    model = joblib.load(MODEL_PATH)

if os.path.exists(CATEGORY_ENCODING_PATH):
    with open(CATEGORY_ENCODING_PATH, 'r') as f:
        category_mapping = json.load(f)

if os.path.exists(NAME_ENCODING_PATH):
    with open(NAME_ENCODING_PATH, 'r') as f:
        name_mapping = json.load(f)

def home(request):
    print(MODEL_PATH)
    print("Model loaded:", model is not None)
    """Public home page - no login required"""
    return render(request, "app/home.html")

@login_required
def detector(request):
    """Fraud detection page - requires login"""
    return render(request, "app/detector.html", {
        'categories': category_mapping.keys(),
        'names': name_mapping.keys()
    })

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('detector')
    else:
        form = UserCreationForm()
    return render(request, "app/register.html", {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('detector')
    else:
        form = AuthenticationForm()
    return render(request, "app/login.html", {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def predict(request):
    if request.method == 'POST':
        # Get data from form
        name_str = request.POST.get('name')
        amount = float(request.POST.get('amount', 0))
        category_str = request.POST.get('category')
        
        # Use encoded values from mapping
        name_val = name_mapping.get(name_str, 0)
        category_val = category_mapping.get(category_str, 0)
        
        # Prepare feature vector
        features = pd.DataFrame([[name_val, amount, category_val]], 
                               columns=['Full Name', 'Amount', 'Category'])
        
        prediction = model.predict(features)[0]
        result = "Fraudulent" if prediction == 1 else "Legitimate"
        
        return render(request, "app/detector.html", {
            'categories': category_mapping.keys(),
            'names': name_mapping.keys(),
            'prediction': result,
            'name': name_str,
            'amount': amount,
            'category': category_str
        })
    return redirect('detector')
