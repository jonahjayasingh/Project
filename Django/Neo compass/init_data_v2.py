import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'neo_compass.settings')
django.setup()

from core.models import User, StudentProfile, Domain

# Create HOD
if not User.objects.filter(username='hod').exists():
    User.objects.create_superuser('hod', 'hod@example.com', 'admin123', role='hod')
    print("HOD created: hod / admin123")

# Create Mentor
if not User.objects.filter(username='mentor1').exists():
    mentor = User.objects.create_user('mentor1', 'mentor@example.com', 'admin123', role='mentor')
    print("Mentor created: mentor1 / admin123")
    
# Create Student
if not User.objects.filter(username='student1').exists():
    student = User.objects.create_user('student1', 'student@example.com', 'admin123', role='student')
    # StudentProfile is created via signal or manually in view, but let's ensure it here
    StudentProfile.objects.get_or_create(user=student)
    print("Student created: student1 / admin123")

# Create a Domain
if not Domain.objects.exists():
    Domain.objects.create(name='Web Development', description='Master HTML, CSS, and JS.')
    print("Domain 'Web Development' created")
