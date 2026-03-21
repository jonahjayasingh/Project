from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database.db import get_db
from models.user import User
<<<<<<< HEAD
from schemas.user_schema import UserCreate, UserOut, Token
=======
from schemas.user_schema import UserCreate, UserUpdate, UserOut, Token
>>>>>>> fac2c57 (add)
from services.auth_service import verify_password, get_password_hash, create_access_token, SECRET_KEY, ALGORITHM
from jose import JWTError, jwt

router = APIRouter(prefix="/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user

@router.post("/register", response_model=UserOut)
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user.password)
    new_user = User(
        name=user.name,
        email=user.email,
        phone=user.phone,
        location=user.location,
        hashed_password=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/profile", response_model=UserOut)
def get_profile(current_user: User = Depends(get_current_user)):
    return current_user
<<<<<<< HEAD
=======

@router.put("/profile", response_model=UserOut)
def update_profile(user_update: UserUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user_update.name is not None:
        current_user.name = user_update.name
    if user_update.phone is not None:
        current_user.phone = user_update.phone
    if user_update.location is not None:
        current_user.location = user_update.location
    if user_update.profile_image is not None:
        current_user.profile_image = user_update.profile_image
    if user_update.password:
        current_user.hashed_password = get_password_hash(user_update.password)
    
    db.commit()
    db.refresh(current_user)
    return current_user

@router.get("/profile-stats")
def get_profile_stats(user_id: int = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    from models.payment import Payment
    from models.pet import Pet
    
    target_user_id = user_id if user_id else current_user.id
    
    # Adopted pets = pets where user paid for contact unlock
    adopted_count = db.query(Payment).filter(
        Payment.user_id == target_user_id,
        Payment.payment_type == "contact_unlock",
        Payment.status == "completed"
    ).count()
    
    listings_count = db.query(Pet).filter(Pet.owner_id == target_user_id).count()
    
    return {
        "adopted": adopted_count,
        "listings": listings_count,
        "favorites": 0
    }

@router.get("/user/{user_id}", response_model=UserOut)
def get_user_profile(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
>>>>>>> fac2c57 (add)
