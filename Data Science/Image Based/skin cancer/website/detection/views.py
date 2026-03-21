import os
import random
import numpy as np
import tensorflow as tf
from PIL import Image
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.conf import settings
from .forms import SkinImageForm
from .models import Prediction

# Cache for the model
MODEL = None

def get_model():
    global MODEL
    if MODEL is None:
        model_path = os.path.join(settings.BASE_DIR, 'static', 'model', 'skin_cancer_model.keras')
        try:
            MODEL = tf.keras.models.load_model(model_path)
            print(f"Model loaded successfully from {model_path}")
        except Exception as e:
            print(f"Error loading model: {e}")
            return None
    return MODEL


def predict_skin_disease(image_input):
    model = get_model()
    if model is None:
        return "Model Error", 0.0

    try:
        # Ensure class names match training order EXACTLY
        class_names = [
            'Basal Cell Carcinoma',
            "Healthy Skin",
            'Melanoma',
            'Squamous Cell Carcinoma'
        ]

        # Load image (supports file path or file object)
        if hasattr(image_input, "read"):
            img = Image.open(image_input)
        else:
            img = Image.open(str(image_input))

        img = img.convert('RGB')

        img = img.resize((224, 224))  # changed from 244 → 224

        # Convert to array
        img_array = np.array(img, dtype=np.float32)

        # Add batch dimension
        img_array = np.expand_dims(img_array, axis=0)

        # Preprocess for EfficientNet
        img_array = tf.keras.applications.efficientnet.preprocess_input(img_array)

        # Prediction
        predictions = model.predict(img_array, verbose=0)

        if predictions.shape[-1] > 1:
            score = predictions[0]
        else:
            # Binary case fallback
            score = np.array([1 - predictions[0][0], predictions[0][0]])

        # Get result
        result_idx = int(np.argmax(score))
        result_label = class_names[result_idx]

        confidence = float(score[result_idx]) * 100

        return result_label, round(confidence, 2)

    except Exception as e:
        print(f"Prediction error: {e}")
        return "Detection Failed", 0.0
def home(request):
    return render(request, 'detection/home.html')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def dashboard(request):
    predictions = Prediction.objects.filter(user=request.user).order_by('-created_at')
    if request.method == 'POST':
        form = SkinImageForm(request.POST, request.FILES)
        if form.is_valid():
            prediction_obj = form.save(commit=False)
            prediction_obj.user = request.user
            
            # Predict using the uploaded image data directly before saving to DB
            result, confidence = predict_skin_disease(request.FILES['image'])
            
            prediction_obj.result = result
            prediction_obj.confidence = confidence
            prediction_obj.save()
            
            return redirect('dashboard')
    else:
        form = SkinImageForm()
    
    return render(request, 'detection/dashboard.html', {
        'form': form,
        'predictions': predictions
    })
