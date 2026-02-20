import os
import joblib
import re
import nltk
from django.conf import settings
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

# Set NLTK data path
local_nltk_path = os.path.join(settings.BASE_DIR.parent, "nltk_data")
nltk.data.path.append(local_nltk_path)

# Load model and vectorizer
MODEL_PATH = os.path.join(settings.BASE_DIR.parent, "cyberbullying_model.pkl")
VECTORIZER_PATH = os.path.join(settings.BASE_DIR.parent, "tfidf_vectorizer.pkl")

model = joblib.load(MODEL_PATH)
vectorizer = joblib.load(VECTORIZER_PATH)

stop_words = set(stopwords.words("english"))
lemmatizer = WordNetLemmatizer()

def preprocess_text(text):
    # remove URLs, mentions, numbers, punctuation
    text = re.sub(r"http\S+|www\S+|@\w+|\d+", "", text)
    text = re.sub(r"[^\w\s]", "", text)
    text = text.lower()

    tokens = word_tokenize(text)
    tokens = [
        lemmatizer.lemmatize(word)
        for word in tokens
        if word not in stop_words and len(word) > 2
    ]

    return " ".join(tokens)

def is_bullying(text):
    if not text:
        return False
    cleaned = preprocess_text(text)
    vec = vectorizer.transform([cleaned])
    prediction = model.predict(vec)
    return bool(prediction[0] == 1)
