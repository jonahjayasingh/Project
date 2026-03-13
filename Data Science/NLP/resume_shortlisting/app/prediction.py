import joblib
import pandas as pd
import os
from django.conf import settings

# Load model once
MODEL_PATH = os.path.join(settings.BASE_DIR, 'models', 'fake_job_model.joblib')
_model = None

def get_model():
    global _model
    if _model is None:
        _model = joblib.load(MODEL_PATH)
    return _model

def predict_fake_job(job_post):
    """
    Predicts if a job post is fake or real based on the trained model.
    """
    model = get_model()
    
    # Prepare combined text field
    # The model was trained on: ['job_title', 'company', 'location', 'skills']
    skills_str = " ".join(job_post.skills) if isinstance(job_post.skills, list) else str(job_post.skills)
    combined_text = f"{job_post.job_title} {job_post.company} {job_post.location} {skills_str}"
    
    # Map job_type to match training expectations if necessary
    # In training: Part-time, Contract (6 months), etc.
    # In DB: Full-Time, Part-Time, Contract, Internship, Remote
    job_type = job_post.job_type
    
    # Handle is_remote based on job_type
    is_remote = "Yes" if job_type == "Remote" else "No"
    
    # Create DataFrame for prediction
    # Columns: ['combined_text', 'job_type', 'experience', 'is_remote']
    input_data = pd.DataFrame([{
        'combined_text': combined_text,
        'job_type': job_type,
        'experience': job_post.experience,
        'is_remote': is_remote
    }])
    
    # Predict
    prediction = model.predict(input_data)[0]
    
    # Return True if fake (1), False if real (0)
    return bool(prediction)
