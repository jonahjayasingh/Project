from sqlalchemy.orm import Session
from database.db import SessionLocal, engine, Base
from models.user import User
from models.pet import Pet, PetMedia
from models.message import Message
from models.payment import Payment
from services.auth_service import get_password_hash
import datetime

def seed_db():
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    # Check if admin already exists
    admin_email = "admin@example.com"
    admin = db.query(User).filter(User.email == admin_email).first()
    
    if not admin:
        print("Creating admin user...")
        admin = User(
            name="Super Admin",
            email=admin_email,
            phone="1234567890",
            location="New York",
            hashed_password=get_password_hash("1"),
            is_admin=True
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
    else:
        print("Admin user already exists.")

    # Add dummy pets if none exist
    if db.query(Pet).count() == 0:
        print("Adding dummy pets...")
        dummy_pets = [
            {
                "name": "Buddy",
                "breed": "Golden Retriever",
                "age": "2 years",
                "gender": "Male",
                "category": "Dog",
                "description": "Friendly and energetic Golden Retriever looking for a home.",
                "location": "New York, USA",
                "is_featured": True
            },
            {
                "name": "Luna",
                "breed": "Siamese",
                "age": "1 year",
                "gender": "Female",
                "category": "Cat",
                "description": "Calm and affectionate Siamese cat.",
                "location": "New York, USA",
                "is_featured": False
            },
            {
                "name": "Rocky",
                "breed": "German Shepherd",
                "age": "3 years",
                "gender": "Male",
                "category": "Dog",
                "description": "Loyal and protective German Shepherd.",
                "location": "Brooklyn, NY",
                "is_featured": True
            },
            {
                "name": "Sky",
                "breed": "Cockatiel",
                "age": "6 months",
                "gender": "Female",
                "category": "Bird",
                "description": "Lovely singing cockatiel.",
                "location": "Queens, NY",
                "is_featured": False
            },
            {
                "name": "Bella",
                "breed": "French Bulldog",
                "age": "1.5 years",
                "gender": "Female",
                "category": "Dog",
                "description": "Small and playful French Bulldog.",
                "location": "Manhattan, NY",
                "is_featured": False
            }
        ]

        for p_data in dummy_pets:
            pet = Pet(
                owner_id=admin.id,
                **p_data
            )
            db.add(pet)
            db.commit()
            db.refresh(pet)
            
            # Add a dummy media entry for each
            media = PetMedia(
                pet_id=pet.id,
                file_type="image",
                file_url="https://images.unsplash.com/photo-1543466835-00a7907e9de1?auto=format&fit=crop&q=80&w=500" # Placeholder
            )
            db.add(media)
            db.commit()

        print("Dummy data seeded successfully.")
    else:
        print("Pets already exist in database.")

    db.close()

if __name__ == "__main__":
    seed_db()
