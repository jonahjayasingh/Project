from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from app.models import JobPost   # <-- replace 'company' with your app name
from datetime import date, timedelta
import random

class Command(BaseCommand):
    help = "Seed the database with dummy JobPost data"

    def handle(self, *args, **kwargs):
        user, _ = User.objects.get_or_create(username="Jonah", defaults={"password": "1"})

        job_titles = ["Software Engineer", "Data Analyst", "Project Manager", "UI/UX Designer", "DevOps Engineer"]
        companies = ["TechCorp", "DataWorks", "BuildIt Inc.", "DesignHub", "Cloudify"]
        locations = ["New York", "San Francisco", "Chicago", "Remote", "Austin"]
        job_types = ["Full-Time", "Part-Time", "Internship", "Contract", "Freelance"]
        experiences = ["Entry Level", "Mid Level", "Senior Level", "Executive"]

        for i in range(30):
            JobPost.objects.create(
                user=user,
                job_title=random.choice(job_titles),
                company=random.choice(companies),
                location=random.choice(locations),
                job_type=random.choice(job_types),
                experience=random.choice(experiences),
                description="This is a sample job description for testing.",
                last_date=date.today() + timedelta(days=random.randint(10, 60)),
                salary=f"${random.randint(40, 120)}k",
                is_active=True,
            )

        self.stdout.write(self.style.SUCCESS("✅ Successfully seeded 10 dummy jobs"))
