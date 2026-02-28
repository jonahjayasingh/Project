import os
import django
import sys

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

from accounts.models import User

def create_admin():
    print("--- Kalyanakumar Admin Creation Tool ---")
    
    username = input("Enter Admin Username [admin]: ") or "admin"
    email = input("Enter Admin Email [admin@kalyanakumar.com]: ") or "admin@kalyanakumar.com"
    password = input("Enter Admin Password [admin123]: ") or "admin123"
    confirm_password = input("Confirm Admin Password: ") or "admin123"

    if password != confirm_password:
        print("Error: Passwords do not match.")
        return

    if User.objects.filter(username=username).exists():
        print(f"Error: User '{username}' already exists. Attempting to promote to ADMIN...")
        user = User.objects.get(username=username)
        user.role = 'ADMIN'
        user.is_staff = True
        user.is_superuser = True
        user.save()
        print(f"Successfully promoted '{username}' to ADMIN.")
    else:
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
            role='ADMIN'
        )
        print(f"\nSUCCESS: Admin user '{username}' created successfully!")
        print(f"Username: {username}")
        print(f"Role: {user.role}")
        print(f"Superuser Status: {user.is_superuser}")

if __name__ == "__main__":
    try:
        create_admin()
    except KeyboardInterrupt:
        print("\nOperation cancelled.")
        sys.exit(0)
    except Exception as e:
        print(f"\nAn error occurred: {e}")
