import os
import django
import sys

# Add the project directory to the sys.path
sys.path.append(os.getcwd())

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User
from app.models import PatientProfile

def seed_patients():
    dummy_patients = [
        {"name": "John Doe", "email": "john@example.com", "username": "john_p", "age": 30, "gender": "Male", "address": "123 Main St", "phone": "1234567890"},
        {"name": "Jane Smith", "email": "jane@example.com", "username": "jane_p", "age": 25, "gender": "Female", "address": "456 Oak Ave", "phone": "9876543210"},
    ]

    password = "1"

    for p_data in dummy_patients:
        if not User.objects.filter(username=p_data["username"]).exists():
            user = User.objects.create_user(
                username=p_data["username"],
                email=p_data["email"],
                password=password
            )
            PatientProfile.objects.create(
                user=user,
                full_name=p_data["name"],
                whatsapp_number=p_data["phone"],
                address=p_data["address"],
                age=p_data["age"],
                gender=p_data["gender"]
            )
            print(f"Created Patient: {p_data['name']} (Username: {p_data['username']})")
        else:
            print(f"Skipping: User {p_data['username']} already exists.")

if __name__ == "__main__":
    print("Seeding dummy patient data...")
    seed_patients()
    print("Seeding complete! Password for all patients is '1'.")
