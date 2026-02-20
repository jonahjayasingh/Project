import django
import os
import sys

# Add the project directory to the sys.path
sys.path.append(os.getcwd())

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from app.models import LabAssistant
from django.contrib.auth.models import User

def approve_existing_labs():
    labs = LabAssistant.objects.all()
    for lab in labs:
        lab.is_approved = True
        lab.save()
        print(f"Approved lab: {lab.lab_name} ({lab.user.username})")

if __name__ == "__main__":
    approve_existing_labs()
