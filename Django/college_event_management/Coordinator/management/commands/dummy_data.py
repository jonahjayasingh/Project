from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from Coordinator.models import Events, EventRegister, Profile
from faker import Faker
import random


class Command(BaseCommand):
    help = (
        "Registers all students for events with specific event types "
        "('Exhibition' or 'Community outreach'). Creates dummy profiles if missing."
    )

    def handle(self, *args, **options):
        fake = Faker("en_IN")
        branches = ["CSE", "ECE", "ME", "CE", "EEE", "IT"]
        years = ["First", "Second", "Third"]
        event_types = ["Exhibition", "Community outreach"]

        # Step 1: Fetch eligible events
        events = Events.objects.filter(event_type__in=event_types)
        if not events.exists():
            self.stdout.write(self.style.WARNING(
                f"No events found with event_type in {event_types}."
            ))
            return

        self.stdout.write(self.style.SUCCESS(
            f"Found {events.count()} eligible events of types {', '.join(event_types)}."
        ))

        # Step 2: Get all users with Profile type 'Student' (or create if missing)
        all_users = list(User.objects.all())
        if not all_users:
            self.stdout.write(self.style.WARNING("No users found in the database."))
            return

        students = []
        for user in all_users:
            profile, _ = Profile.objects.get_or_create(
                user=user,
                defaults={
                    "type": "Student",
                    "phone": fake.phone_number(),
                    "address": fake.address(),
                    "branch": random.choice(branches),
                    "year": random.choice(years),
                    "admission_no": fake.bothify(text="ADM####"),
                    "registration_no": fake.bothify(text="REG####"),
                    "dob": fake.date_of_birth(minimum_age=18, maximum_age=25),
                },
            )
            if profile.type == "Student":
                students.append(user)

        self.stdout.write(self.style.SUCCESS(f"Found {len(students)} students to register."))

        # Step 3: Register each student for random eligible event(s)
        for user in students:
            event = random.choice(events)
            register, created = EventRegister.objects.get_or_create(
                user=user,
                event=event,
                defaults={
                    "project_title": fake.sentence(nb_words=4),
                    "project_description": fake.paragraph(nb_sentences=3),
                    "project_members": ", ".join(fake.first_name() for _ in range(random.randint(2, 4))),
                    "branch": profile.branch,
                },
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f"Registered {user.username} for {event.event_name} ({event.event_type})")
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f"{user.username} already registered for {event.event_name}")
                )

        self.stdout.write(self.style.SUCCESS("All students registered successfully!"))
