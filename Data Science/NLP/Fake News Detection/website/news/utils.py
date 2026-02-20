import joblib
import os
import re
import nltk
from nltk.corpus import stopwords
from django.conf import settings

# Setup NLTK
NLTK_DATA = os.path.join(settings.BASE_DIR.parent, "nltk_data")
if NLTK_DATA not in nltk.data.path:
    nltk.data.path.append(NLTK_DATA)

try:
    stop_words = set(stopwords.words('english'))
except LookupError:
    nltk.download('stopwords', download_dir=NLTK_DATA)
    stop_words = set(stopwords.words('english'))

MODEL_PATH = os.path.join(settings.BASE_DIR, "model", "fake_news_detection.pkl")

_model_cache = None

def clean_text(text):
    if not isinstance(text, str):
        return ""
    text = re.sub(r'[^a-zA-Z]', ' ', text.lower())
    tokens = text.split()
    tokens = [w for w in tokens if w not in stop_words]
    return " ".join(tokens)

def get_model():
    global _model_cache
    if _model_cache is None:
        if os.path.exists(MODEL_PATH):
            try:
                _model_cache = joblib.load(MODEL_PATH)
            except Exception as e:
                print("Error loading model:", e)
                return None
        else:
            return None
    return _model_cache

def predict(text):
    data = get_model()

    if data is None:
        return "Model not found", 0

    # Handle both cases:
    # 1) data is dict with model & vectorizer
    # 2) data is only model
    if isinstance(data, dict):
        model = data.get("model")
        vectorizer = data.get("vectorizer")
    else:
        # If only model was saved, this will fail unless you load vectorizer separately
        print("Warning: Pickle contains only model. Vectorizer missing.")
        return "Vectorizer missing", 0

    if model is None or vectorizer is None:
        return "Invalid model file", 0

    cleaned = clean_text(text)
    transformed = vectorizer.transform([cleaned])

    prediction = model.predict(transformed)[0]

    # Probability handling (safe)
    try:
        prob = model.predict_proba(transformed)[0]
        confidence = max(prob)
    except:
        confidence = 0.5

    label = "REAL" if prediction == 1 else "FAKE"
    return label, float(confidence)
