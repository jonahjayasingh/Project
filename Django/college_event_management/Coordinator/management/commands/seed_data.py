import requests
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from faker import Faker
import random

from Coordinator.models import Gallery, Events

fake = Faker()

EVENT_TYPES = [
    "Cultural & Arts",
    "Academic & Technical",
    "Sports & Fitness",
    "Social & Community",
    "Special Celebrations",
]

LOCATIONS = [
    "Main Auditorium",
    "Sports Complex",
    "College Ground",
    "Conference Hall",
    "Cultural Stage",
]

class Command(BaseCommand):
    help = "Seed database with dummy Events and Gallery data using Faker (User ID 1)"

    def handle(self, *args, **kwargs):
        try:
            user = User.objects.get(id=1)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR("❌ User with ID=1 does not exist. Please create it first."))
            return

        # --- Seed Events ---
        for i in range(0):
            event_name = fake.catch_phrase()
            event = Events.objects.create(
                user=user,
                event_name=event_name,
                event_date=timezone.now() + timezone.timedelta(days=random.randint(1, 60)),
                event_location=random.choice(LOCATIONS),
                event_description=fake.paragraph(nb_sentences=5),
            )

            # Download random placeholder image
            img_url = f"https://picsum.photos/seed/event{i}/600/400"
            img_temp = NamedTemporaryFile(delete=True)
            img_temp.write(requests.get(img_url).content)
            img_temp.flush()
            event.event_image.save(f"event{i}.jpg", File(img_temp), save=True)

            self.stdout.write(self.style.SUCCESS(f"✅ Created Event: {event_name}"))

        # --- Seed Gallery ---
        for i in range(50):
            caption = fake.sentence(nb_words=6)
            gallery = Gallery.objects.create(
                user=user,
                caption=caption,
                gallery_type=random.choice(EVENT_TYPES),
            )

            # Download random placeholder image
            img_url = f"https://picsum.photos/seed/gallery{i}/500/500"
            img_temp = NamedTemporaryFile(delete=True)
            img_temp.write(requests.get(img_url).content)
            img_temp.flush()
            gallery.image.save(f"gallery{i}.jpg", File(img_temp), save=True)

            self.stdout.write(self.style.SUCCESS(f"🖼️ Added Gallery Image: {caption}"))
