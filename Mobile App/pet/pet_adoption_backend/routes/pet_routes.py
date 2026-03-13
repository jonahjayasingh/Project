from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from database.db import get_db
from models.user import User
from schemas.pet_schema import PetCreate, PetOut, PetUpdate
from services.pet_service import create_pet, get_pets, get_pet_by_id, update_pet, delete_pet, save_media
from routes.auth_routes import get_current_user

router = APIRouter(prefix="/pets", tags=["pets"])

@router.post("/", response_model=PetOut)
def add_pet(pet: PetCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return create_pet(db, pet, current_user.id)

@router.get("/", response_model=List[PetOut])
def list_pets(
    skip: int = 0, 
    limit: int = 100, 
    breed: Optional[str] = None, 
    category: Optional[str] = None, 
    location: Optional[str] = None,
    lat: Optional[float] = None,
    lon: Optional[float] = None,
    radius: Optional[float] = 10.0,
    db: Session = Depends(get_db)
):
    return get_pets(db, skip, limit, breed, category, location, lat, lon, radius)

@router.get("/{id}", response_model=PetOut)
def get_pet(id: int, db: Session = Depends(get_db)):
    db_pet = get_pet_by_id(db, id)
    if not db_pet:
        raise HTTPException(status_code=404, detail="Pet not found")
    return db_pet

@router.put("/{id}", response_model=PetOut)
def update_pet_route(id: int, pet_update: PetUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_pet = get_pet_by_id(db, id)
    if not db_pet:
        raise HTTPException(status_code=404, detail="Pet not found")
    if db_pet.owner_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to update this pet")
    return update_pet(db, id, pet_update)

@router.delete("/{id}")
def delete_pet_route(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_pet = get_pet_by_id(db, id)
    if not db_pet:
        raise HTTPException(status_code=404, detail="Pet not found")
    if db_pet.owner_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to delete this pet")
    delete_pet(db, id)
    return {"message": "Pet deleted successfully"}

@router.post("/{id}/media")
async def upload_pet_media(
    id: int, 
    file: UploadFile = File(...), 
    file_type: str = Query(..., pattern="^(image|video)$"),
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    db_pet = get_pet_by_id(db, id)
    if not db_pet:
        raise HTTPException(status_code=404, detail="Pet not found")
    if db_pet.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to upload media for this pet")
    return save_media(db, id, file, file_type)
