import os
import joblib
import json
import pandas as pd
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .forms import PredictionForm

# Paths to model and encoders
PARENT_DIR = os.path.dirname(settings.BASE_DIR)
MODEL_PATH = os.path.join(PARENT_DIR, 'drug_detection.pkl')
ENCODER_PATH = os.path.join(PARENT_DIR, 'label_encoders.json')

# Load model and encoders once at startup
try:
    model = joblib.load(MODEL_PATH)
    with open(ENCODER_PATH, 'r') as f:
        encoders = json.load(f)
except Exception as e:
    model = None
    encoders = None
    print(f"Error loading model/encoders: {e}")

@login_required
def dashboard(request):
    return render(request, 'detection/dashboard.html', {'form': PredictionForm()})

@login_required
def predict(request):
    if request.method == 'POST':
        form = PredictionForm(request.POST)
        if form.is_valid() and model is not None:
            # Prepare data for prediction
            data = form.cleaned_data
            
            # Encode 'sex'
            sex_mapping = {val: i for i, val in enumerate(encoders['sex'])}
            data['sex'] = sex_mapping.get(data['sex'], 0)
            
            # Create DataFrame
            df = pd.DataFrame([data])
            
            # Feature engineering to match fit time
            df["AST_ALT_ratio"] = df["AST"] / (df["ALT"] + 1)
            df["pulse_pressure"] = df["systolic_bp"] - df["diastolic_bp"]
            df["tachycardia_index"] = df["heart_rate"] / (df["systolic_bp"] + 1)
            df["renal_stress"] = df["creatinine"] * df["hours_since_use"]
            df["acid_load"] = abs(7.4 - df["blood_pH"]) * df["hours_since_use"]
            df["stim_index"] = df["heart_rate"] * df["systolic_bp"]
            
            # Select and order features as seen at fit time (dropping hours_since_use)
            features = ['age', 'sex', 'heart_rate', 'systolic_bp', 'diastolic_bp', 'respiratory_rate', 
                        'oxygen_saturation', 'body_temperature', 'blood_pH', 'ALT', 'AST', 
                        'creatinine', 'glucose', 'WBC_count', 'AST_ALT_ratio', 'pulse_pressure', 
                        'tachycardia_index', 'renal_stress', 'acid_load', 'stim_index']
            df = df[features]
            
            # Predict
            prediction_idx = model.predict(df)[0]
            prediction_label = encoders['drug_detected'][prediction_idx]
            
            # Get probabilities if available
            try:
                probs = model.predict_proba(df)[0]
                results = zip(encoders['drug_detected'], [round(p * 100, 2) for p in probs])
            except:
                results = None

            return render(request, 'detection/dashboard.html', {
                'form': form,
                'prediction': prediction_label,
                'results': results
            })
    else:
        form = PredictionForm()
        
    return render(request, 'detection/dashboard.html', {'form': form})
