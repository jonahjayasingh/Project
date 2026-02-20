import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User
from app.models import LabAssistant

def create_lab(username, email, password):
    if not User.objects.filter(username=username).exists():
        user = User.objects.create_user(username=username, email=email, password=password)
        LabAssistant.objects.create(
            user=user, 
            lab_name="City Lab", 
            license_number="LIC-12345",
            is_approved=True
        )
        print(f"Lab User {username} created and approved successfully!")
    else:
        print(f"User {username} already exists.")

if __name__ == "__main__":
    # Using the credentials you provided for testing
    create_lab("lab1@gmail.com", "lab1@gmail.com", "lab1@123")
