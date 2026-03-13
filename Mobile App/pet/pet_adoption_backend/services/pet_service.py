from sqlalchemy.orm import Session
from models.pet import Pet, PetMedia
from schemas.pet_schema import PetCreate, PetUpdate
import os
import shutil
import uuid

def create_pet(db: Session, pet: PetCreate, owner_id: int):
    db_pet = Pet(**pet.dict(), owner_id=owner_id)
    db.add(db_pet)
    db.commit()
    db.refresh(db_pet)
    return db_pet

def get_pets(db: Session, skip: int = 0, limit: int = 100, breed: str = None, category: str = None, location: str = None, lat: float = None, lon: float = None, radius: float = 10.0):
    query = db.query(Pet)
    if breed:
        query = query.filter(Pet.breed.ilike(f"%{breed}%"))
    if category:
        query = query.filter(Pet.category == category)
    if location:
        query = query.filter(Pet.location.ilike(f"%{location}%"))
    
    if lat is not None and lon is not None:
        # Simple bounding box for location filtering (approx 1 degree = 111km)
        # For a small radius like 10km, approx 0.09 degrees
        offset = radius / 111.0
        query = query.filter(
            Pet.latitude >= lat - offset,
            Pet.latitude <= lat + offset,
            Pet.longitude >= lon - offset,
            Pet.longitude <= lon + offset
        )
    
    # Sort by featured first, then by date
    return query.order_by(Pet.is_featured.desc(), Pet.created_at.desc()).offset(skip).limit(limit).all()

def get_pet_by_id(db: Session, pet_id: int):
    return db.query(Pet).filter(Pet.id == pet_id).first()

def update_pet(db: Session, pet_id: int, pet_update: PetUpdate):
    db_pet = get_pet_by_id(db, pet_id)
    if not db_pet:
        return None
    for key, value in pet_update.dict(exclude_unset=True).items():
        setattr(db_pet, key, value)
    db.commit()
    db.refresh(db_pet)
    return db_pet

def delete_pet(db: Session, pet_id: int):
    db_pet = get_pet_by_id(db, pet_id)
    if db_pet:
        db.delete(db_pet)
        db.commit()
        return True
    return False

def save_media(db: Session, pet_id: int, file, file_type: str):
    # Ensure upload directories exist
    upload_dir = f"uploads/{file_type}s"
    os.makedirs(upload_dir, exist_ok=True)
    
    file_extension = file.filename.split(".")[-1]
    file_name = f"{uuid.uuid4()}.{file_extension}"
    file_path = os.path.join(upload_dir, file_name)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    db_media = PetMedia(pet_id=pet_id, file_type=file_type, file_url=file_path)
    db.add(db_media)
    db.commit()
    return db_media
