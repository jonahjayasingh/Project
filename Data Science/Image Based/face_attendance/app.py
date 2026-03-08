import os
import cv2
import numpy as np
import face_recognition
import sqlite3
from sqlalchemy import func
from datetime import datetime, date, timedelta
from flask import Flask, render_template, request, redirect, flash, url_for, session, Response
from uuid import uuid4
from werkzeug.security import generate_password_hash, check_password_hash

# Import database models and session
from model import Admin, Attendance, StudentData, engine, Session

app = Flask(__name__)
app.secret_key = 'super_secret_key_change_me'
TRAINING_PATH = "static/Training images"

if not os.path.exists(TRAINING_PATH):
    os.makedirs(TRAINING_PATH)

# Global camera object to share between routes
class VideoCamera:
    def __init__(self):
        self.video = cv2.VideoCapture(0)
        self.encodeListKnown = []
        self.classNames = []
        self.load_known_faces()

    def __del__(self):
        self.video.release()

    def load_known_faces(self):
        images = []
        self.classNames = []
        if os.path.exists(TRAINING_PATH):
            for cl in os.listdir(TRAINING_PATH):
                img = cv2.imread(f'{TRAINING_PATH}/{cl}')
                if img is not None:
                    images.append(img)
                    self.classNames.append(os.path.splitext(cl)[0])
        
        self.encodeListKnown = []
        for img in images:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            encs = face_recognition.face_encodings(img)
            if encs:
                self.encodeListKnown.append(encs[0])

    def get_frame(self, mode='none'):
        success, image = self.video.read()
        if not success:
            return None

        if mode == 'recognize' and self.encodeListKnown:
            imgS = cv2.resize(image, (0, 0), None, 0.25, 0.25)
            imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)
            facesCurFrame = face_recognition.face_locations(imgS)
            encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

            for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
                faceDis = face_recognition.face_distance(self.encodeListKnown, encodeFace)
                if len(faceDis) > 0:
                    matchIndex = np.argmin(faceDis)
                    if faceDis[matchIndex] < 0.50:
                        name = self.classNames[matchIndex].upper()
                        # Mark attendance in background-ish via local logic
                        self.mark_attendance_internal(name)
                    else:
                        name = 'UNKNOWN'
                else:
                    name = 'UNKNOWN'

                y1, x2, y2, x1 = [v * 4 for v in faceLoc]
                color = (0, 255, 0) if name != 'UNKNOWN' else (0, 0, 255)
                cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
                cv2.putText(image, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 0.8, (255, 255, 255), 2)

        ret, jpeg = cv2.imencode('.jpg', image)
        return jpeg.tobytes()

    def mark_attendance_internal(self, name):
        # We need a separate session here
        db = Session()
        try:
            now = datetime.now()
            today = now.date()
            
            # Find the student by name
            student = db.query(StudentData).filter(StudentData.name == name).first()
            if not student:
                print(f"Student {name} not found in database")
                return
            
            # Check if student already has a record for today
            exists = db.query(Attendance).filter(
                Attendance.student_id == student.registration_id, 
                Attendance.Date == today
            ).first()
            
            if exists:
                # Already marked for today - do nothing
                print(f"Attendance already marked for {name} today")
            else:
                # Create a new record - first time seen today
                new_att = Attendance(student_id=student.registration_id, Date=today, Time=now.time())
                db.add(new_att)
                db.commit()
                print(f"✓ Attendance MARKED for {name} at {now.time().strftime('%I:%M:%S %p')}")
        except Exception as e:
            print(f"Error in internal mark: {e}")
            db.rollback()
        finally:
            db.close()

# Shared camera instance
global_camera = None

def get_camera():
    global global_camera
    if global_camera is None:
        global_camera = VideoCamera()
    return global_camera

def get_session():
    return Session()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_session()
        try:
            admin = db.query(Admin).filter_by(username=username).first()
            if admin and check_password_hash(admin.password, password):
                session['admin'] = username
                flash("Logged in successfully!", "success")
                return redirect(url_for('dashboard'))
            else:
                flash("Invalid credentials", "error")
        finally:
            db.close()
    return render_template('login.html')

# Admin registration disabled - use create_admin.py to create administrators
# @app.route('/register', methods=["GET", "POST"])
# def register():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#         db = get_session()
#         try:
#             if db.query(Admin).filter_by(username=username).first():
#                 flash("Username already exists", "error")
#             else:
#                 new_admin = Admin(username=username, password=generate_password_hash(password))
#                 db.add(new_admin)
#                 db.commit()
#                 flash("Success! Please login.", "success")
#                 return redirect(url_for('login'))
#         finally:
#             db.close()
#     return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('home'))

@app.route('/dashboard')
def dashboard():
    if 'admin' not in session: return redirect(url_for('login'))
    db = get_session()
    stats = {
        'total_students': db.query(StudentData).count(),
        'today_attendance': db.query(Attendance).filter(Attendance.Date == date.today()).count()
    }
    db.close()
    return render_template('dashboard.html', stats=stats)

@app.route('/register_student')
def register_student():
    if 'admin' not in session: return redirect(url_for('login'))
    return render_template('enroll.html')

@app.route('/enroll', methods=['POST'])
def enroll_step1():
    reg_id = request.form["reg_id"]
    name = request.form['full_name']
    return render_template('capture.html', reg_id=reg_id, name=name)

@app.route('/save_enrollment', methods=['POST'])
def save_enrollment():
    reg_id = request.form["reg_id"]
    name = request.form["name"]
    
    cam = get_camera()
    success, frame = cam.video.read()
    if success:
        img_path = os.path.join(TRAINING_PATH, f"{name}{uuid4()}.png")
        cv2.imwrite(img_path, frame)
        db = get_session()
        try:
            new_student = StudentData(registration_id=reg_id, name=name, image=img_path)
            db.add(new_student)
            db.commit()
            cam.load_known_faces() # Reload database for recognition
            return render_template('message.html', title="Success", message=f"{name} enrolled!", url="/studentdata")
        except Exception as e:
            flash(f"Error: {e}", "error")
        finally:
            db.close()
    return redirect(url_for('register_student'))

@app.route('/start_recognition')
def start_recognition():
    return render_template('recognize.html')

def gen_frames(camera, mode):
    while True:
        frame = camera.get_frame(mode)
        if frame is None:
            break
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    mode = request.args.get('mode', 'none')
    return Response(gen_frames(get_camera(), mode),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/data')
def data():
    db = get_session()
    today = date.today()
    students = db.query(StudentData).all()
    # Distinct records for today
    records = db.query(Attendance).filter(Attendance.Date == today).all()
    record_map = {r.Name.upper(): r for r in records}
    
    final_rows = []
    present_count = 0
    absent_count = 0
    
    for s in students:
        if s.name.upper() in record_map:
            final_rows.append(record_map[s.name.upper()])
            present_count += 1
        else:
            # Create a simple object for absent students (for display only)
            absent_record = type('obj', (object,), {
                'Name': s.name,
                'Date': today,
                'Time': None
            })()
            final_rows.append(absent_record)
            absent_count += 1
    
    stats = {
        'present': present_count,
        'absent': absent_count,
        'total': len(students)
    }
    
    db.close()
    return render_template('attendance_data.html', rows=final_rows, filter_type='date', stats=stats)

@app.route('/my_attendance')
def my_attendance():
    filter_type = request.args.get("filter_type", "all")
    filter_value = request.args.get("filter_value")
    db = get_session()
    
    if filter_type == "date" and filter_value:
        # Show all students with status for a specific date
        query_date = datetime.strptime(filter_value, "%Y-%m-%d").date()
        students = db.query(StudentData).all()
        records = db.query(Attendance).filter(Attendance.Date == query_date).all()
        record_map = {r.Name.upper(): r for r in records}
        
        final_rows = []
        present_count = 0
        absent_count = 0
        
        for s in students:
            if s.name.upper() in record_map:
                final_rows.append(record_map[s.name.upper()])
                present_count += 1
            else:
                # Create a simple object for absent students (for display only)
                absent_record = type('obj', (object,), {
                    'Name': s.name,
                    'Date': query_date,
                    'Time': None
                })()
                final_rows.append(absent_record)
                absent_count += 1
        
        stats = {
            'present': present_count,
            'absent': absent_count,
            'total': len(students)
        }
        
        db.close()
        return render_template('attendance_data.html', rows=final_rows, filter_type=filter_type, stats=stats)

    # For other filters, show all students with attendance frequency
    students = db.query(StudentData).all()
    query = db.query(Attendance)
    
    # Determine date range
    start_date = None
    end_date = date.today()
    
    if filter_type == "week" and filter_value:
        dt = datetime.strptime(filter_value, "%Y-%m-%d").date()
        start_date = dt - timedelta(days=dt.weekday())
        end_date = start_date + timedelta(days=6)
        query = query.filter(Attendance.Date.between(start_date, end_date))
    elif filter_type == "month" and filter_value:
        dt = datetime.strptime(filter_value, "%Y-%m-%d").date()
        query = query.filter(func.strftime('%m', Attendance.Date) == dt.strftime('%m'))
        query = query.filter(func.strftime('%Y', Attendance.Date) == dt.strftime('%Y'))
        # Calculate start and end of month
        start_date = dt.replace(day=1)
        if dt.month == 12:
            end_date = dt.replace(year=dt.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            end_date = dt.replace(month=dt.month + 1, day=1) - timedelta(days=1)
    else:
        # All time - get earliest attendance date
        earliest = db.query(func.min(Attendance.Date)).scalar()
        start_date = earliest if earliest else date.today()

    records = query.all()
    
    # Calculate total days in period (for week/month only)
    if start_date and filter_type in ['week', 'month']:
        total_days = (end_date - start_date).days + 1
    else:
        total_days = None  # For all-time, we'll count actual attendance days
    
    # Group attendance by student and count unique days
    student_days = {}
    for record in records:
        name_upper = record.Name.upper()
        if name_upper not in student_days:
            student_days[name_upper] = set()
        student_days[name_upper].add(record.Date)
    
    # Build final rows with attendance summary
    final_rows = []
    present_count = 0
    absent_count = 0
    
    for s in students:
        name_upper = s.name.upper()
        days_present = len(student_days.get(name_upper, set()))
        
        if days_present > 0:
            # Create a summary attendance record
            latest_date = max(student_days[name_upper])
            days_absent = total_days - days_present if total_days else 0
            
            # Create custom object with attendance summary
            summary = type('obj', (object,), {
                'Name': s.name,
                'Date': latest_date,
                'Time': None,  # Will be replaced with summary text
                'days_present': days_present,
                'days_absent': days_absent,
                'is_summary': True
            })()
            final_rows.append(summary)
            present_count += 1
        else:
            # Student never attended
            summary = type('obj', (object,), {
                'Name': s.name,
                'Date': end_date,
                'Time': None,
                'days_present': 0,
                'days_absent': total_days if total_days else 0,
                'is_summary': True
            })()
            final_rows.append(summary)
            absent_count += 1
    
    stats = {
        'present': present_count,
        'absent': absent_count,
        'total': len(students)
    }
    
    db.close()
    return render_template('attendance_data.html', rows=final_rows, filter_type=filter_type, stats=stats, is_summary_view=True)

@app.route("/studentdata")
def student_data():
    if 'admin' not in session: return redirect(url_for('login'))
    db = get_session()
    students = db.query(StudentData).all()
    student_list = [(s.registration_id, s.name) for s in students]
    db.close()
    return render_template("students.html", students=student_list)



@app.route("/delete_student/<int:registration_id>")
def delete_student(registration_id):
    if 'admin' not in session: return redirect(url_for('login'))
    db = get_session()
    s = db.query(StudentData).filter_by(registration_id=registration_id).first()
    if s:
        if os.path.exists(s.image): os.remove(s.image)
        db.delete(s)
        db.commit()
        get_camera().load_known_faces()
    db.close()
    return redirect(url_for("student_data"))

@app.route("/edit_student/<int:registration_id>")
def edit_student_form(registration_id):
    if 'admin' not in session: return redirect(url_for('login'))
    db = get_session()
    s = db.query(StudentData).filter_by(registration_id=registration_id).first()
    data = (s.registration_id, s.name) if s else None
    db.close()
    return render_template("edit_student.html", student=data)

@app.route("/update_student/<int:old_registration_id>", methods=["POST"])
def update_student(old_registration_id):
    if 'admin' not in session: return redirect(url_for('login'))
    db = get_session()
    s = db.query(StudentData).filter_by(registration_id=old_registration_id).first()
    if s:
        s.registration_id = request.form.get("registration_id")
        s.name = request.form.get("name")
        db.commit()
    db.close()
    return redirect(url_for("student_data"))

if __name__ == '__main__':
    from model import Base, engine
    Base.metadata.create_all(engine)
    
    # Trigger camera initialization on the main thread
    # This is required on macOS to handle permission requests correctly.
    print("Pre-initializing camera on main thread to handle macOS permissions...")
    try:
        get_camera()
        print("Camera initialized successfully.")
    except Exception as e:
        print(f"Could not initialize camera on main thread: {e}")

    app.run(host='0.0.0.0', port=5001, debug=True, threaded=True)