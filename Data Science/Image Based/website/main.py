from flask import Flask, render_template, request, redirect, url_for, flash,jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.mobilenet_v3 import preprocess_input
from PIL import Image

import os,io

class_names = ['Acne And Rosacea Photos', 'Actinic Keratosis Basal Cell Carcinoma And Other Malignant Lesions', 'Atopic Dermatitis Photos', 'Ba  Cellulitis', 'Ba Impetigo', 'Benign', 'Bullous Disease Photos', 'Cellulitis Impetigo And Other Bacterial Infections', 'Eczema Photos', 'Exanthems And Drug Eruptions', 'Fu Athlete Foot', 'Fu Nail Fungus', 'Fu Ringworm', 'Hair Loss Photos Alopecia And Other Hair Diseases', 'Herpes Hpv And Other Stds Photos', 'Light Diseases And Disorders Of Pigmentation', 'Lupus And Other Connective Tissue Diseases', 'Malignant', 'Melanoma Skin Cancer Nevi And Moles', 'Rashes']


UPLOAD_FOLDER = 'uploads'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
model = load_model("static/tf_model.keras")

app.secret_key = "supersecretkey"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

# Setup Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

def load_and_preprocess(img_path, target_size=(128,128)):
    img = image.load_img(img_path, target_size=target_size)
    x = image.img_to_array(img)          # Convert to array
    x = np.expand_dims(x, axis=0)        # Add batch dimension
    x = preprocess_input(x)              # Apply MobileNetV3 preprocessing
    return x



def predict_image(img_path):
    x = load_and_preprocess(img_path)
    preds = model.predict(x)
    pred_class_idx = np.argmax(preds, axis=1)[0]
    pred_class_prob = preds[0][pred_class_idx]
    pred_class_name = class_names[pred_class_idx]

    return pred_class_name,pred_class_prob


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/register",methods=["GET","POST"])
def register():
    if request.method == "POST":
        usename = request.form.get("username")
        password = request.form.get("password")
        c_password = request.form.get("confirmPassword")
        if password != c_password:
            flash("Password do not match")
            return redirect(url_for("register"))
        hashed_password = generate_password_hash(password, method="pbkdf2:sha256")
        new_user = User(username=usename, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/login",methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("dashboard"))
        else:
            flash("Login Unsuccessful. Please check username and password")
            return redirect(url_for("login"))
    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")



@app.route('/predict', methods=['POST'])
def predict():
    if 'skinImage' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['skinImage']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    # Save temporarily
    os.makedirs("uploads", exist_ok=True)
    temp_path = os.path.join("uploads", file.filename)
    file.save(temp_path)

    # Predict
    predicted_class, confidence = predict_image(temp_path)

    print(predicted_class)
    print(confidence)
    # Clean up file
    os.remove(temp_path)

    return render_template("dashboard.html",predicted_class=predicted_class,confidence=confidence)

def get_additional_info(disease_class):
    """Returns additional information about the predicted disease"""
    info = {
        'melanoma': {
            'description': 'A serious form of skin cancer that develops in melanocytes.',
            'severity': 'High',
            'recommendation': 'Consult a dermatologist immediately.',
            'tag': 'malignant'
        },
        'psoriasis': {
            'description': 'A chronic autoimmune condition that causes rapid skin cell buildup.',
            'severity': 'Medium',
            'recommendation': 'See a dermatologist for treatment options.',
            'tag': 'inflammatory'
        },
        'eczema': {
            'description': 'A condition that makes skin red and itchy.',
            'severity': 'Low',
            'recommendation': 'Use moisturizers and avoid irritants.',
            'tag': 'inflammatory'
        },
        'ringworm': {
            'description': 'A fungal infection that causes a ring-shaped rash.',
            'severity': 'Medium',
            'recommendation': 'Antifungal treatment re`commended.',
            'tag': 'infectious'
        },
        'acne': {
            'description': 'A skin condition that occurs when hair follicles become clogged.',
            'severity': 'Low',
            'recommendation': 'Over-the-counter treatments may help.',
            'tag': 'benign'
        }
    }
    return info.get(disease_class, {})


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)


