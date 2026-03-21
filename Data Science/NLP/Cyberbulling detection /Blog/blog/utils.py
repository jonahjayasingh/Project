import os
import re
import joblib
import nltk

from django.conf import settings
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

# ---------------------------------------------------
# Base Paths
# ---------------------------------------------------

BASE_DIR = settings.BASE_DIR

NLTK_DATA_PATH = os.path.join(BASE_DIR, "nltk_data")
MODEL_DIR = os.path.join(BASE_DIR, "models")

MODEL_PATH = os.path.join(MODEL_DIR, "cyberbullying_model.pkl")
VECTORIZER_PATH = os.path.join(MODEL_DIR, "tfidf_vectorizer.pkl")

# ---------------------------------------------------
# Ensure directories exist
# ---------------------------------------------------

os.makedirs(NLTK_DATA_PATH, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)

# ---------------------------------------------------
# Configure NLTK to use local directory
# ---------------------------------------------------

nltk.data.path.append(NLTK_DATA_PATH)

# ---------------------------------------------------
# Required NLTK resources
# ---------------------------------------------------

required_packages = [
    "punkt",
    "punkt_tab",
    "stopwords",
    "wordnet",
    "omw-1.4"
]

for package in required_packages:
    try:
        nltk.data.find(package)
    except LookupError:
        nltk.download(package, download_dir=NLTK_DATA_PATH)

# ---------------------------------------------------
# Load Model + Vectorizer
# ---------------------------------------------------

model = joblib.load(MODEL_PATH)
vectorizer = joblib.load(VECTORIZER_PATH)

# ---------------------------------------------------
# NLP Tools
# ---------------------------------------------------

stop_words = set(stopwords.words("english"))
lemmatizer = WordNetLemmatizer()

# ---------------------------------------------------
# Text Preprocessing Function
# ---------------------------------------------------

def preprocess_text(text):

    # Remove URLs
    text = re.sub(r"http\S+|www\S+", "", text)

    # Remove mentions
    text = re.sub(r"@\w+", "", text)

    # Remove numbers
    text = re.sub(r"\d+", "", text)

    # Remove punctuation
    text = re.sub(r"[^\w\s]", "", text)

    # Convert to lowercase
    text = text.lower()

    # Tokenization
    tokens = word_tokenize(text)

    # Remove stopwords + lemmatize
    tokens = [
        lemmatizer.lemmatize(word)
        for word in tokens
        if word not in stop_words and len(word) > 2
    ]

    return " ".join(tokens)

# ---------------------------------------------------
# Cyberbullying Detection
# ---------------------------------------------------

def is_bullying(text):

    if not text:
        return False

    cleaned_text = preprocess_text(text)

    vectorized_text = vectorizer.transform([cleaned_text])

    prediction = model.predict(vectorized_text)

    return bool(prediction[0] == 1)