from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FloatField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
import joblib
import os
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-this'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# Load ML model
try:
    model = joblib.load('models/rf_aqi_model.pkl')
except:
    model = None
    print("Warning: Model not found. Predictions will not work.")

# Database Models
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    predictions = db.relationship('Prediction', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Prediction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    pm25 = db.Column(db.Float, nullable=False)
    pm10 = db.Column(db.Float, nullable=False)
    no = db.Column(db.Float, nullable=False)
    no2 = db.Column(db.Float, nullable=False)
    nh3 = db.Column(db.Float, nullable=False)
    co = db.Column(db.Float, nullable=False)
    so2 = db.Column(db.Float, nullable=False)
    o3 = db.Column(db.Float, nullable=False)
    benzene = db.Column(db.Float, nullable=False)
    toluene = db.Column(db.Float, nullable=False)
    xylene = db.Column(db.Float, nullable=False)
    predicted_aqi = db.Column(db.String(50), nullable=False)
    confidence = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Forms
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', 
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class PredictionForm(FlaskForm):
    pm25 = FloatField('PM2.5', validators=[DataRequired()])
    pm10 = FloatField('PM10', validators=[DataRequired()])
    no = FloatField('NO', validators=[DataRequired()])
    no2 = FloatField('NO2', validators=[DataRequired()])
    nh3 = FloatField('NH3', validators=[DataRequired()])
    co = FloatField('CO', validators=[DataRequired()])
    so2 = FloatField('SO2', validators=[DataRequired()])
    o3 = FloatField('O3', validators=[DataRequired()])
    benzene = FloatField('Benzene', validators=[DataRequired()])
    toluene = FloatField('Toluene', validators=[DataRequired()])
    xylene = FloatField('Xylene', validators=[DataRequired()])
    submit = SubmitField('Predict AQI')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Account created successfully! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=True)
            next_page = request.args.get('next')
            flash('Login successful!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login failed. Check email and password.', 'danger')
    
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

@app.route('/predict', methods=['GET', 'POST'])
@login_required
def predict():
    form = PredictionForm()
    
    if form.validate_on_submit():
        # Prepare input data
        input_data = [[
            form.pm25.data, form.pm10.data, form.no.data, form.no2.data,
            form.nh3.data, form.co.data, form.so2.data,
            form.o3.data, form.benzene.data, form.toluene.data, form.xylene.data
        ]]
        
        # Make prediction
        if model:
            prediction = model.predict(input_data)[0]
            probabilities = model.predict_proba(input_data)[0]
            confidence = max(probabilities) * 100
            
            # AQI categories
            aqi_categories = {
                0: 'Good',
                1: 'Moderate',
                2: 'Poor',
                3: 'Unhealthy',
                4: 'Very Unhealthy',
                5: 'Hazardous'
            }
            
            predicted_category = aqi_categories.get(prediction, 'Unknown')
            
            # Save prediction to database
            prediction_record = Prediction(
                user_id=current_user.id,
                pm25=form.pm25.data,
                pm10=form.pm10.data,
                no=form.no.data,
                no2=form.no2.data,
                nh3=form.nh3.data,
                co=form.co.data,
                so2=form.so2.data,
                o3=form.o3.data,
                benzene=form.benzene.data,
                toluene=form.toluene.data,
                xylene=form.xylene.data,
                predicted_aqi=predicted_category,
                confidence=confidence
            )
            db.session.add(prediction_record)
            db.session.commit()
            
            return render_template('results.html', 
                                 prediction=predicted_category,
                                 confidence=round(confidence, 2),
                                 probabilities=probabilities.tolist())
        else:
            flash('Prediction model not available.', 'danger')
    
    return render_template('predict.html', form=form)

@app.route('/history')
@login_required
def history():
    predictions = Prediction.query.filter_by(user_id=current_user.id)\
                    .order_by(Prediction.created_at.desc())\
                    .limit(10)\
                    .all()
    return render_template('history.html', predictions=predictions)

@app.route('/api/predict', methods=['POST'])
@login_required
def api_predict():
    data = request.json
    
    if not data or not model:
        return jsonify({'error': 'Invalid request or model not available'}), 400
    
    try:
        input_data = [[
            data['pm25'], data['pm10'], data['no'], data['no2'],
            data['nh3'], data['co'], data['so2'],
            data['o3'], data['benzene'], data['toluene'], data['xylene']
        ]]
        
        prediction = model.predict(input_data)[0]
        probabilities = model.predict_proba(input_data)[0]
        confidence = max(probabilities) * 100
        
        aqi_categories = {
            0: 'Good',
            1: 'Moderate',
            2: 'Poor',
            3: 'Unhealthy',
            4: 'Very Unhealthy',
            5: 'Hazardous'
        }
        
        return jsonify({
            'prediction': aqi_categories.get(prediction, 'Unknown'),
            'confidence': round(confidence, 2),
            'probabilities': probabilities.tolist(),
            'category_code': int(prediction)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

# Create database tables
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)