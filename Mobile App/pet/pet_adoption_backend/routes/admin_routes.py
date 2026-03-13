from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database.db import get_db
from models.user import User
from models.pet import Pet
from schemas.user_schema import UserOut
from schemas.pet_schema import PetOut
from routes.auth_routes import get_current_user

router = APIRouter(prefix="/admin", tags=["admin"])

def check_admin(current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

@router.get("/users", response_model=List[UserOut])
def list_users(db: Session = Depends(get_db), admin: User = Depends(check_admin)):
    return db.query(User).all()

@router.get("/pets", response_model=List[PetOut])
def list_all_pets(db: Session = Depends(get_db), admin: User = Depends(check_admin)):
    return db.query(Pet).all()

@router.delete("/pet/{id}")
def admin_delete_pet(id: int, db: Session = Depends(get_db), admin: User = Depends(check_admin)):
    db_pet = db.query(Pet).filter(Pet.id == id).first()
    if not db_pet:
        raise HTTPException(status_code=404, detail="Pet not found")
    db.delete(db_pet)
    db.commit()
    return {"message": "Pet deleted by admin"}

@router.post("/ban-user/{user_id}")
def ban_user(user_id: int, db: Session = Depends(get_db), admin: User = Depends(check_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # In a real app, you'd have an is_banned column
    # For now, we'll just delete the user as a "ban"
    db.delete(user)
    db.commit()
    return {"message": "User banned and removed"}
