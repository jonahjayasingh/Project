import os
import django
import sys

# Add the project directory to the sys.path
sys.path.append(os.getcwd())

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User
from app.models import LabAssistant

def seed_labs():
    dummy_labs = [
        {"name": "Central Diagnostics", "license": "LIC-99001", "approved": True, "username": "central_lab"},
        {"name": "Health Plus Laboratory", "license": "LIC-99002", "approved": True, "username": "healthplus"},
        {"name": "Precision Pathology", "license": "LIC-99003", "approved": False, "username": "precision_path"},
        {"name": "Swift Scan Center", "license": "LIC-99004", "approved": False, "username": "swift_scan"},
        {"name": "Modern Lab Services", "license": "LIC-99005", "approved": True, "username": "modern_lab"},
        {"name": "BioTech Research Lab", "license": "LIC-99006", "approved": False, "username": "biotech"},
    ]

    password = "1"

    for lab_data in dummy_labs:
        if not User.objects.filter(username=lab_data["username"]).exists():
            user = User.objects.create_user(
                username=lab_data["username"],
                email=f"{lab_data['username']}@example.com",
                password=password
            )
            LabAssistant.objects.create(
                user=user,
                lab_name=lab_data["name"],
                license_number=lab_data["license"],
                is_approved=lab_data["approved"]
            )
            status = "Approved" if lab_data["approved"] else "Pending"
            print(f"Created {status} Lab: {lab_data['name']} (Username: {lab_data['username']})")
        else:
            print(f"Skipping: User {lab_data['username']} already exists.")

if __name__ == "__main__":
    print("Seeding dummy laboratory data...")
    seed_labs()
    print("Seeding complete! Password for all labs is '1'.")
