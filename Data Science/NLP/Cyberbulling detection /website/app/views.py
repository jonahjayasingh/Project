from django.shortcuts import render
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.models import User

import joblib
import os
import nltk

local_nltk_path = os.path.join(os.getcwd(), "nltk_data")
os.makedirs(local_nltk_path, exist_ok=True)

nltk.data.path.append(local_nltk_path)

nltk.download("punkt", download_dir=local_nltk_path)
nltk.download("stopwords", download_dir=local_nltk_path)
nltk.download("punkt_tab", download_dir=local_nltk_path)
nltk.download("wordnet", download_dir=local_nltk_path)
import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

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

model = joblib.load("static/models/cyberbullying_model.pkl")
vectorizer = joblib.load("static/models/tfidf_vectorizer.pkl")

def predict_cyberbullying(texts):
    texts_clean = [preprocess_text(t) for t in texts]
    texts_vec = vectorizer.transform(texts_clean)
    return model.predict(texts_vec)


# Create your views here.
def index(request):
    return render(request, "index.html")

def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password1"]
        confirm_password = request.POST["password2"]

        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return render(request, "register.html")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return render(request, "register.html")

        user = User.objects.create_user(username=username, password=password)
        user.save()

        messages.success(request, "Account created successfully. Please login.")
        return render(request, "login.html")

    return render(request, "register.html")

def userlogin(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Login successful.")
            return render(request, "index.html")
        else:
            messages.error(request, "Invalid username or password.")
            return render(request, "login.html")

    return render(request, "login.html")

def userlogout(request):
    logout(request)
    messages.success(request, "Logout successful.")
    return render(request, "index.html")

def predict(request):
    if request.method == "POST":
        text = request.POST["text"]
        prediction = predict_cyberbullying([text])[0]
        if prediction == 1:
            prediction = "Cyberbullying"
        else:
            prediction = "Not Cyberbullying"
        return render(request, "predict.html", {"prediction": prediction})
    return render(request, "predict.html")
