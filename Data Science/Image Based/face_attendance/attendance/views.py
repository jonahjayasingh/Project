from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import StreamingHttpResponse, HttpResponse
from django.conf import settings
from .models import StudentData, Attendance
from .camera import get_camera
import os
import cv2
from datetime import datetime, date, timedelta
from uuid import uuid4
from django.db.models import Count, Min, Max

TRAINING_PATH = os.path.join(settings.BASE_DIR, "static/Training images")

def home(request):
    return render(request, 'index.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Logged in successfully!")
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid credentials")
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required(login_url='login')
def dashboard(request):
    total_students = StudentData.objects.count()
    today_attendance = Attendance.objects.filter(date=date.today()).count()
    rate = round((today_attendance / total_students * 100), 1) if total_students > 0 else 0
    stats = {
        'total_students': total_students,
        'today_attendance': today_attendance,
        'rate': rate
    }
    return render(request, 'dashboard.html', {'stats': stats})

@login_required(login_url='login')
def register_student(request):
    return render(request, 'enroll.html')

@login_required(login_url='login')
def enroll_step1(request):
    reg_id = request.POST.get("reg_id")
    name = request.POST.get('full_name')
    return render(request, 'capture.html', {'reg_id': reg_id, 'name': name})

@login_required(login_url='login')
def save_enrollment(request):
    reg_id = request.POST.get("reg_id")
    name = request.POST.get("name")
    
    cam = get_camera()
    success, frame = cam.video.read()
    if success:
        if not os.path.exists(TRAINING_PATH):
            os.makedirs(TRAINING_PATH)
        
        img_filename = f"{name}{uuid4()}.png"
        img_path = os.path.join(TRAINING_PATH, img_filename)
        cv2.imwrite(img_path, frame)
        
        # Save relative path for database compatibility or full path as before
        # The original code stored full path: os.path.join(TRAINING_PATH, f"{name}{uuid4()}.png")
        try:
            StudentData.objects.create(registration_id=reg_id, name=name, image=img_path)
            cam.load_known_faces() # Reload database for recognition
            return render(request, 'message.html', {
                'title': "Success", 
                'message': f"{name} enrolled!", 
                'url': "/studentdata"
            })
        except Exception as e:
            messages.error(request, f"Error: {e}")
    
    return redirect('register_student')

@login_required(login_url='login')
def start_recognition(request):
    today = date.today()
    present_students = Attendance.objects.filter(date=today).select_related('student').order_by('-time')
    return render(request, 'recognize.html', {'present_students': present_students})

def gen_frames(camera, mode):
    while True:
        frame = camera.get_frame(mode)
        if frame is None:
            break
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def video_feed(request):
    mode = request.GET.get('mode', 'none')
    return StreamingHttpResponse(gen_frames(get_camera(), mode),
                                 content_type='multipart/x-mixed-replace; boundary=frame')

@login_required(login_url='login')
def data(request):
    today = date.today()
    students = StudentData.objects.all()
    records = Attendance.objects.filter(date=today)
    record_map = {r.student.name.upper(): r for r in records}
    
    final_rows = []
    present_count = 0
    absent_count = 0
    
    for s in students:
        if s.name.upper() in record_map:
            final_rows.append(record_map[s.name.upper()])
            present_count += 1
        else:
            absent_record = {
                'Name': s.name,
                'date': today,
                'time': None
            }
            final_rows.append(absent_record)
            absent_count += 1
    
    stats = {
        'present': present_count,
        'absent': absent_count,
        'total': len(students)
    }
    
    return render(request, 'attendance_data.html', {'rows': final_rows, 'filter_type': 'date', 'stats': stats})

@login_required(login_url='login')
def my_attendance(request):
    filter_type = request.GET.get("filter_type", "all")
    filter_value = request.GET.get("filter_value")
    
    if filter_type == "date" and filter_value:
        query_date = datetime.strptime(filter_value, "%Y-%m-%d").date()
        students = StudentData.objects.all()
        records = Attendance.objects.filter(date=query_date)
        record_map = {r.student.name.upper(): r for r in records}
        
        final_rows = []
        present_count = 0
        absent_count = 0
        
        for s in students:
            if s.name.upper() in record_map:
                final_rows.append(record_map[s.name.upper()])
                present_count += 1
            else:
                absent_record = {
                    'Name': s.name,
                    'date': query_date,
                    'time': None
                }
                final_rows.append(absent_record)
                absent_count += 1
        
        stats = {
            'present': present_count,
            'absent': absent_count,
            'total': len(students)
        }
        
        return render(request, 'attendance_data.html', {'rows': final_rows, 'filter_type': filter_type, 'stats': stats})

    students = StudentData.objects.all()
    query = Attendance.objects.all()
    
    start_date = None
    end_date = date.today()
    
    if filter_type == "week" and filter_value:
        dt = datetime.strptime(filter_value, "%Y-%m-%d").date()
        start_date = dt - timedelta(days=dt.weekday())
        end_date = start_date + timedelta(days=6)
        query = query.filter(date__range=(start_date, end_date))
    elif filter_type == "month" and filter_value:
        dt = datetime.strptime(filter_value, "%Y-%m-%d").date()
        query = query.filter(date__month=dt.month, date__year=dt.year)
        start_date = dt.replace(day=1)
        if dt.month == 12:
            end_date = dt.replace(year=dt.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            end_date = dt.replace(month=dt.month + 1, day=1) - timedelta(days=1)
    else:
        earliest = Attendance.objects.aggregate(Min('date'))['date__min']
        start_date = earliest if earliest else date.today()

    records = query.all()
    
    if start_date and filter_type in ['week', 'month']:
        total_days = (end_date - start_date).days + 1
    else:
        total_days = None
    
    student_days = {}
    for record in records:
        name_upper = record.student.name.upper()
        if name_upper not in student_days:
            student_days[name_upper] = set()
        student_days[name_upper].add(record.date)
    
    final_rows = []
    present_count = 0
    absent_count = 0
    
    for s in students:
        name_upper = s.name.upper()
        days_present = len(student_days.get(name_upper, set()))
        
        if days_present > 0:
            latest_date = max(student_days[name_upper])
            days_absent = total_days - days_present if total_days else 0
            
            summary = {
                'Name': s.name,
                'date': latest_date,
                'time': None,
                'days_present': days_present,
                'days_absent': days_absent,
                'is_summary': True
            }
            final_rows.append(summary)
            present_count += 1
        else:
            summary = {
                'Name': s.name,
                'date': end_date,
                'time': None,
                'days_present': 0,
                'days_absent': total_days if total_days else 0,
                'is_summary': True
            }
            final_rows.append(summary)
            absent_count += 1
    
    stats = {
        'present': present_count,
        'absent': absent_count,
        'total': len(students)
    }
    
    return render(request, 'attendance_data.html', {
        'rows': final_rows, 
        'filter_type': filter_type, 
        'stats': stats, 
        'is_summary_view': True
    })

@login_required(login_url='login')
def student_data(request):
    students = StudentData.objects.all()
    return render(request, "students.html", {'students': students})

@login_required(login_url='login')
def delete_student(request, registration_id):
    student = get_object_or_404(StudentData, registration_id=registration_id)
    if os.path.exists(student.image):
        os.remove(student.image)
    student.delete()
    get_camera().load_known_faces()
    return redirect("student_data")

@login_required(login_url='login')
def edit_student_form(request, registration_id):
    student = get_object_or_404(StudentData, registration_id=registration_id)
    return render(request, "edit_student.html", {'student': student})

@login_required(login_url='login')
def update_student(request, old_registration_id):
    student = get_object_or_404(StudentData, registration_id=old_registration_id)
    if request.method == 'POST':
        student.registration_id = request.POST.get("registration_id")
        student.name = request.POST.get("name")
        student.save()
    return redirect("student_data")
