import io
import random
import requests
import json
from faker import Faker
from PIL import Image, ImageDraw

API_BASE = "http://localhost:8000/website"
NUM_RECORDS = 20
fake = Faker()


def generate_image_bytes(text: str = "Image"):
    img = Image.new("RGB", (400, 250),
        color=(random.randint(100,255), random.randint(100,255), random.randint(100,255)))
    draw = ImageDraw.Draw(img)
    draw.text((20, 100), text, fill=(0, 0, 0))
    img_bytes = io.BytesIO()
    img.save(img_bytes, format="JPEG")
    img_bytes.seek(0)
    return img_bytes


def post_form(endpoint: str, data: dict, files: dict = None):
    url = f"{API_BASE}{endpoint}"
    try:
        resp = requests.post(url, data=data, files=files, timeout=10) if files else requests.post(url, json=data, timeout=10)
        if resp.status_code in (200, 201):
            print(f"✅ Created: {endpoint}")
        else:
            print(f"⚠️ Failed ({resp.status_code}): {endpoint} → {resp.text}")
    except Exception as e:
        print(f"❌ Error sending to {endpoint}: {e}")


def seed_courses():
    print("📘 Seeding courses...")
    for _ in range(NUM_RECORDS):
        image = generate_image_bytes("Course")
        data = {
            "course_name": fake.catch_phrase(),
            "course_description": fake.text(100),
            "course_price": random.randint(100, 1000),
            "course_difficulty": random.choice(["Beginner", "Intermediate", "Advanced"]),
            "course_duration": random.choice(["2 weeks", "1 month", "3 months"]),
            "user_id": random.randint(1, 5),
        }
        files = {"course_thumbnail": ("course.jpg", image, "image/jpeg")}
        post_form("/courses/courses", data, files)


def seed_gallery():
    print("🖼️ Seeding gallery...")
    for _ in range(NUM_RECORDS):
        image = generate_image_bytes("Gallery")
        data = {"gallery_title": fake.sentence(nb_words=3), "user_id": random.randint(1, 5)}
        files = {"gallery_image": ("gallery.jpg", image, "image/jpeg")}
        post_form("/gallery/gallery", data, files)


def seed_services():
    print("🛠️ Seeding services...")
    for _ in range(NUM_RECORDS):
        image = generate_image_bytes("Service")
        data = {
            "name": fake.job(),
            "description": fake.text(120),
            "key_points": json.dumps([fake.word() for _ in range(3)]),
            "user_id": random.randint(1, 5),
        }
        files = {"image": ("service.jpg", image, "image/jpeg")}
        post_form("/services/services", data, files)


def seed_domains():
    print("🌐 Seeding project domains...")
    for _ in range(NUM_RECORDS):
        image = generate_image_bytes("Domain")
        data = {
            "name": fake.word().capitalize() + " Domain",
            "description": fake.text(80),
            "user_id": random.randint(1, 5),
        }
        files = {"image": ("domain.jpg", image, "image/jpeg")}
        post_form("/project-domains/domains", data, files)


def seed_portfolio():
    print("💼 Seeding portfolio...")
    for _ in range(NUM_RECORDS):
        image = generate_image_bytes("Portfolio")
        data = {
            "title": fake.company(),
            "description": fake.text(100),
            "project_type": random.choice(["Web", "Mobile", "AI", "Design"]),
            "project_url": fake.url(),
            "user_id": random.randint(1, 5),
        }
        files = {"project_image": ("portfolio.jpg", image, "image/jpeg")}
        post_form("/portfolios/portfolio", data, files)


def seed_contacts():
    print("☎️ Seeding company contacts...")
    for _ in range(1):
        data = {
            "phone1": fake.random_int(min=1000000000, max=9999999999),
            "phone2": fake.random_int(min=1000000000, max=9999999999),
            "email": fake.email(),
            "whatsapp": fake.random_int(min=1000000000, max=9999999999),
            "address": fake.address(),
            "linkedin": fake.url(),
            "twitter": fake.url(),
            "facebook": fake.url(),
            "instagram": fake.url(),
            "youtube": fake.url(),
            "map_embed_url": fake.url(),
            "user_id": random.randint(1, 5),
        }
        post_form("/contacts/contacts", data)


def seed_careers():
    print("💼 Seeding careers...")
    for _ in range(NUM_RECORDS):
        data = {
            "title": fake.job(),
            "description": fake.text(100),
            "location": fake.city(),
            "application_deadline": str(fake.date_this_year()),
            "job_type": random.choice(["Full-time", "Part-time", "Remote"]),
            "experience": random.choice(["1 year", "2 years", "5+ years"]),
            "key_responsibilities": [fake.bs() for _ in range(3)],
            "user_id": random.randint(1, 5),
        }
        post_form("/applicants/careers", data)


if __name__ == "__main__":
    print("🚀 Starting API-based seeding process...")
    seed_courses()
    seed_gallery()
    seed_services()
    seed_domains()
    seed_portfolio()
    seed_contacts()
    seed_careers()
    print("🎉 All data seeded successfully through API endpoints!")
