from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import StreamingHttpResponse, HttpResponse
from django.conf import settings
from .models import StudentData, Attendance, Staff, SystemSettings
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
    today_attendance = Attendance.objects.filter(date=date.today(), status='Present').count()
    rate = round((today_attendance / total_students * 100), 1) if total_students > 0 else 0
    
    # Staff stats
    staff_stats = Staff.objects.annotate(student_count=Count('students'))
    
    # Notification: Long absentees (> 3 days)
    three_days_ago = date.today() - timedelta(days=3)
    long_absentees = []
    all_students = StudentData.objects.all()
    for student in all_students:
        recent_attendance = Attendance.objects.filter(student=student, date__gte=three_days_ago, status='Present').exists()
        if not recent_attendance:
            long_absentees.append(student.name)

    stats = {
        'total_students': total_students,
        'today_attendance': today_attendance,
        'rate': rate,
        'staff_stats': staff_stats,
        'long_absentees': long_absentees
    }
    return render(request, 'dashboard.html', {'stats': stats})

@login_required(login_url='login')
def register_student(request):
    staffs = Staff.objects.all()
    return render(request, 'enroll.html', {'staffs': staffs})

@login_required(login_url='login')
def enroll_step1(request):
    reg_id = request.POST.get("reg_id")
    name = request.POST.get('full_name')
    address = request.POST.get('address')
    dept = request.POST.get('dept')
    staff_id = request.POST.get('staff')
    return render(request, 'capture.html', {
        'reg_id': reg_id, 
        'name': name,
        'address': address,
        'dept': dept,
        'staff_id': staff_id
    })

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
            student = StudentData.objects.create(
                registration_id=reg_id, 
                name=name, 
                image=img_path,
                address=request.POST.get('address'),
                dept=request.POST.get('dept'),
                staff_id=request.POST.get('staff_id')
            )
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
    try:
        while True:
            frame = camera.get_frame(mode)
            if frame is None:
                break
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    finally:
        # Mark sign-out for everyone who attended today when the camera session ends
        try:
            today = date.today()
            now = datetime.now().time()
            # Update all present students' sign out time to current time
            # Only if they haven't been manually signed out or if we want to refresh it
            Attendance.objects.filter(date=today, status='Present').update(sign_out_time=now)
            print(f"✓ All present students SIGNED OUT at {now.strftime('%I:%M %p')} due to camera closure.")
        except Exception as e:
            print(f"Error marking sign-out on camera close: {e}")

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
                'name': s.name,
                'date': today,
                'time': None,
                'sign_out_time': None,
                'status': 'Absent'
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
                    'name': s.name,
                    'date': query_date,
                    'time': None,
                    'sign_out_time': None,
                    'status': 'Absent'
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
    elif filter_type == "range":
        start_str = request.GET.get("start_date")
        end_str = request.GET.get("end_date")
        if start_str and end_str:
            start_date = datetime.strptime(start_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_str, "%Y-%m-%d").date()
            query = query.filter(date__range=(start_date, end_date))
        else:
            start_date = date.today() - timedelta(days=30)
            end_date = date.today()
    else:
        earliest = Attendance.objects.aggregate(Min('date'))['date__min']
        start_date = earliest if earliest else date.today()
        end_date = date.today()

    records = query.all()
    
    if start_date:
        total_days = (end_date - start_date).days + 1
    else:
        total_days = 1
    
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
        
        # 75% Attendance Validation
        percentage = round((days_present / total_days) * 100, 1) if total_days > 0 else 0
        low_attendance = percentage < 75
        days_absent = total_days - days_present

        if days_present > 0:
            latest_date = max(student_days[name_upper])
            summary = {
                'name': s.name,
                'date': latest_date,
                'time': None,
                'sign_out_time': None,
                'status': 'Present',
                'days_present': days_present,
                'days_absent': days_absent,
                'percentage': percentage,
                'low_attendance': low_attendance,
                'is_summary': True
            }
            final_rows.append(summary)
            present_count += 1
        else:
            summary = {
                'name': s.name,
                'date': end_date,
                'time': None,
                'sign_out_time': None,
                'status': 'Absent',
                'days_present': 0,
                'days_absent': days_absent,
                'percentage': percentage,
                'low_attendance': low_attendance,
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
        'is_summary_view': True,
        'start_date': start_date,
        'end_date': end_date
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
    staffs = Staff.objects.all()
    return render(request, "edit_student.html", {'student': student, 'staffs': staffs})

@login_required(login_url='login')
def update_student(request, old_registration_id):
    student = get_object_or_404(StudentData, registration_id=old_registration_id)
    if request.method == 'POST':
        student.registration_id = request.POST.get("registration_id")
        student.name = request.POST.get("name")
        student.address = request.POST.get("address")
        student.dept = request.POST.get("dept")
        staff_id = request.POST.get("staff")
        if staff_id:
            student.staff = Staff.objects.filter(id=staff_id).first()
        student.save()
        messages.success(request, f"Details for {student.name} updated successfully.")
    return redirect("student_data")

@login_required(login_url='login')
def mark_absent_automatically(request):
    try:
        conf = SystemSettings.objects.first()
        if not conf:
            conf = SystemSettings.objects.create()
        
        now = datetime.now()
        start_time = datetime.combine(date.today(), conf.start_time)
        threshold_time = start_time + timedelta(minutes=conf.absent_threshold_minutes)
        
        if now > threshold_time:
            # Mark all students who haven't signed in as absent
            all_students = StudentData.objects.all()
            marked_count = 0
            for student in all_students:
                exists = Attendance.objects.filter(student=student, date=date.today()).exists()
                if not exists:
                    Attendance.objects.create(
                        student=student, 
                        date=date.today(), 
                        time=now.time(), 
                        status='Absent'
                    )
                    marked_count += 1
            messages.success(request, f"{marked_count} absentees marked automatically.")
        else:
            messages.warning(request, f"Too early to mark absentees. Wait until {threshold_time.strftime('%I:%M %p')}")
    except Exception as e:
        messages.error(request, f"Error: {e}")
    
    return redirect('dashboard')

@login_required(login_url='login')
def register_staff(request):
    return render(request, 'enroll_staff.html')

@login_required(login_url='login')
def save_staff(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        dept = request.POST.get('dept')
        email = request.POST.get('email')
        
        try:
            Staff.objects.create(name=name, department=dept, email=email)
            messages.success(request, f"Staff '{name}' enrolled successfully.")
        except Exception as e:
            messages.error(request, f"Error: {e}")
            
    return redirect('dashboard')

@login_required(login_url='login')
def faculty_data(request):
    faculties = Staff.objects.all()
    return render(request, "faculties.html", {'faculties': faculties})

@login_required(login_url='login')
def delete_faculty(request, faculty_id):
    faculty = get_object_or_404(Staff, id=faculty_id)
    faculty.delete()
    messages.success(request, "Faculty member removed successfully.")
    return redirect("faculty_data")

@login_required(login_url='login')
def system_settings(request):
    settings = SystemSettings.objects.first()
    if not settings:
        settings = SystemSettings.objects.create()
        
    if request.method == 'POST':
        start_time_str = request.POST.get('start_time')
        threshold = request.POST.get('threshold')
        
        try:
            settings.start_time = datetime.strptime(start_time_str, "%H:%M").time()
            settings.absent_threshold_minutes = int(threshold)
            settings.save()
            messages.success(request, "System settings updated successfully.")
        except Exception as e:
            messages.error(request, f"Error: {e}")
            
    return render(request, "settings.html", {'settings': settings})

@login_required(login_url='login')
def finalize_attendance(request):
    try:
        today = date.today()
        now = datetime.now().time()
        # Mark all present/absent records for today with the final sign-out time
        Attendance.objects.filter(date=today, sign_out_time__isnull=True).update(sign_out_time=now)
        messages.success(request, f"Daily attendance finalized. All records marked out at {now.strftime('%I:%M %p')}.")
    except Exception as e:
        messages.error(request, f"Error finalizing attendance: {e}")
    return redirect('dashboard')
