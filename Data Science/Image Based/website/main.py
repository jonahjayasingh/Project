from flask import Flask, render_template, request, redirect, url_for, flash,jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from tensorflow import keras


import os

class_names = ['Acne And Rosacea Photos', 'Actinic Keratosis Basal Cell Carcinoma And Other Malignant Lesions', 'Atopic Dermatitis Photos', 'Ba  Cellulitis', 'Ba Impetigo', 'Benign', 'Bullous Disease Photos', 'Cellulitis Impetigo And Other Bacterial Infections', 'Eczema Photos', 'Exanthems And Drug Eruptions', 'Fu Athlete Foot', 'Fu Nail Fungus', 'Fu Ringworm', 'Hair Loss Photos Alopecia And Other Hair Diseases', 'Herpes Hpv And Other Stds Photos', 'Light Diseases And Disorders Of Pigmentation', 'Lupus And Other Connective Tissue Diseases', 'Malignant', 'Melanoma Skin Cancer Nevi And Moles', 'Rashes']

treatment_suggestions = {
    "Acne And Rosacea Photos": "Common approaches include topical retinoids, benzoyl peroxide, oral antibiotics, or azelaic acid. Please consult a dermatologist.",
    "Actinic Keratosis Basal Cell Carcinoma And Other Malignant Lesions": "May require cryotherapy, topical chemotherapy (5-FU), imiquimod, or surgical excision. Urgent dermatologist referral is recommended.",
    "Atopic Dermatitis Photos": "Typically managed with moisturizers, topical corticosteroids, calcineurin inhibitors, and antihistamines. Severe cases need medical care.",
    "Ba  Cellulitis": "Usually treated with oral or IV antibiotics depending on severity. Immediate medical evaluation is advised.",
    "Ba Impetigo": "Managed with topical or oral antibiotics such as mupirocin or cephalexin. A doctor should confirm treatment.",
    "Benign": "Often requires no treatment. Removal may be considered if symptomatic or for cosmetic reasons.",
    "Bullous Disease Photos": "Can involve corticosteroids, immunosuppressants, and wound care. Requires specialist management.",
    "Cellulitis Impetigo And Other Bacterial Infections": "Antibiotics tailored to infection type are typically used. Medical supervision is important.",
    "Eczema Photos": "Moisturizers, topical corticosteroids, and antihistamines are common treatments. Consultation with a doctor is advised.",
    "Exanthems And Drug Eruptions": "Stopping the offending drug, supportive care, antihistamines, and corticosteroids may help. Requires medical review.",
    "Fu Athlete Foot": "Usually treated with topical antifungal creams (e.g., clotrimazole, terbinafine). Persistent cases may need oral antifungals.",
    "Fu Nail Fungus": "Oral antifungals (terbinafine, itraconazole) or topical ciclopirox are commonly used. Requires long-term management.",
    "Fu Ringworm": "Treated with topical antifungals (clotrimazole, terbinafine). Widespread infections may require oral therapy.",
    "Hair Loss Photos Alopecia And Other Hair Diseases": "Options may include minoxidil, finasteride, or corticosteroid injections. Treatment depends on cause.",
    "Herpes Hpv And Other Stds Photos": "Antivirals (acyclovir, valacyclovir) may be used for herpes. HPV lesions may be treated with cryotherapy or topical agents. Specialist evaluation is important.",
    "Light Diseases And Disorders Of Pigmentation": "May involve topical steroids, calcineurin inhibitors, hydroquinone, or phototherapy. Dermatology follow-up is recommended.",
    "Lupus And Other Connective Tissue Diseases": "Managed with immunosuppressants such as hydroxychloroquine or corticosteroids. Requires rheumatology/dermatology care.",
    "Malignant": "Surgical excision, chemotherapy, immunotherapy, or radiation may be required. Immediate oncology/dermatology referral is essential.",
    "Melanoma Skin Cancer Nevi And Moles": "Typically treated with wide excision surgery, immunotherapy, or targeted therapy. Urgent referral to a specialist is critical.",
    "Rashes": "Treatment depends on cause; common options include antihistamines, topical corticosteroids, and emollients. Medical assessment is advised."
}


UPLOAD_FOLDER = 'uploads'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
model = load_model("static/skin_disease_model_tf.keras")

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

def predict_image(img_path, target_size=(224, 224)):
    # Load and preprocess
    img = load_img(img_path, target_size=target_size)
    x = img_to_array(img)
    x = np.expand_dims(x, axis=0)  # add batch dimension
    x = keras.applications.efficientnet.preprocess_input(x)

    # Predict
    preds = model.predict(x)
    pred_class_idx = np.argmax(preds, axis=1)[0]
    pred_class_prob = float(preds[0][pred_class_idx])
    pred_class_name = class_names[pred_class_idx]

    return pred_class_name, pred_class_prob,img


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
@login_required
def dashboard():
    return render_template("dashboard.html")

import base64
import imghdr

@app.route('/predict', methods=['POST'])
@login_required
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
    img_format = imghdr.what(temp_path)
    if img_format is None:
        os.remove(temp_path)
        return jsonify({"error": "Unsupported image format"}), 400

    # Convert image to base64
    with open(temp_path, "rb") as f:
        img_bytes = f.read()
    img_base64 = base64.b64encode(img_bytes).decode("utf-8")

    # Pick correct MIME type
    img_data = f"data:image/{img_format};base64,{img_base64}"

    # Predict
    predicted_class, confidence,img = predict_image(temp_path)
   
    # Clean up file
    os.remove(temp_path)

    return render_template("dashboard.html",predicted_class=predicted_class, treatment= treatment_suggestions[predicted_class],img_data=img_data)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out successfully.", "info")
    return redirect(url_for("login"))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)


