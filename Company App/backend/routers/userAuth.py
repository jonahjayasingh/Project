from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import User, get_db
from schema import UserCreate, UserLogin
from auth import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    user_exists = db.query(User).filter(User.username == user.username).first()
    if user_exists:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    new_user = User(username=user.username, password=hash_password(user.password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User registered successfully", "username": new_user.username}

@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    user_exists = db.query(User).filter(User.username == user.username).first()
    if not user_exists or not verify_password(user.password, user_exists.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}
