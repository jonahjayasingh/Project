import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'placement_system.settings')
django.setup()

from core.models import User, StudentProfile

def create_users():
    """Create all types of users with password '1'"""
    
    users_created = []
    
    # Create Admin user
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@example.com',
            'role': 'admin',
            'is_staff': True,
            'is_superuser': True
        }
    )
    if created:
        admin_user.set_password('1')
        admin_user.save()
        users_created.append(('admin', 'admin', '1', 'Admin'))
        print("✓ Admin user created")
    else:
        admin_user.set_password('1')
        admin_user.save()
        users_created.append(('admin', 'admin', '1', 'Admin'))
        print("✓ Admin user updated")
    
    # Create Student user
    student_user, created = User.objects.get_or_create(
        username='student',
        defaults={
            'email': 'student@example.com',
            'role': 'student'
        }
    )
    if created:
        student_user.set_password('1')
        student_user.save()
        users_created.append(('student', 'student', '1', 'Student'))
        print("✓ Student user created")
    else:
        student_user.set_password('1')
        student_user.save()
        users_created.append(('student', 'student', '1', 'Student'))
        print("✓ Student user updated")
    
    # Create StudentProfile for the student
    student_profile, created = StudentProfile.objects.get_or_create(
        user=student_user,
        defaults={
            'register_number': 'STU001',
            'year_of_study': 3,
            'department': 'Computer Science',
            'is_approved': True  # Auto-approve for testing
        }
    )
    if created:
        print("✓ Student profile created")
    else:
        student_profile.is_approved = True
        student_profile.save()
        print("✓ Student profile updated")
    
    # Create Company user
    company_user, created = User.objects.get_or_create(
        username='company',
        defaults={
            'email': 'company@example.com',
            'role': 'company'
        }
    )
    if created:
        company_user.set_password('1')
        company_user.save()
        users_created.append(('company', 'company', '1', 'Company'))
        print("✓ Company user created")
    else:
        company_user.set_password('1')
        company_user.save()
        users_created.append(('company', 'company', '1', 'Company'))
        print("✓ Company user updated")
    
    # Save credentials to a.txt
    with open('a.txt', 'w') as f:
        f.write("=== Placement Management System - User Credentials ===\n\n")
        for role_type, username, password, role_name in users_created:
            f.write(f"Role: {role_name}\n")
            f.write(f"Username: {username}\n")
            f.write(f"Password: {password}\n")
            f.write("-" * 50 + "\n\n")
    
    print("\n✓ All credentials saved to a.txt")
    print(f"\nTotal users created/updated: {len(users_created)}")

if __name__ == '__main__':
    create_users()
