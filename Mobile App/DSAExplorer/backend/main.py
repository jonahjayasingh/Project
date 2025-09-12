from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from database import Base, engine
from fastapi.security import OAuth2PasswordRequestForm

from auth import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    refresh_access_token,
    get_current_user,
)
from sqlalchemy.orm import Session
from schemas import UserCreate, BookmarkCreate
from models import User, Bookmarks
from crud import get_db, create_user, create_bookmark, get_user_bookmarks
from crud import delete_user_bookmark, get_bookmark_by_id

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"greeting": "Hello"}

@app.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    user_exist = db.query(User).filter(User.username == user.username).first()
    if user_exist:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="User with that name already exists"
        )
    user.password = hash_password(user.password)
    return create_user(db, user)

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == form_data.username).first()
    if not db_user or not verify_password(form_data.password, db_user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Invalid credentials"
        )
    
    access_token = create_access_token(data={"sub": db_user.username})
    refresh_token = create_refresh_token(data={"sub": db_user.username})
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@app.post("/refresh")
def refresh(refresh_token: str):
    """
    Exchange a valid refresh token for a new access token.
    """
    try:
        new_access_token = refresh_access_token(refresh_token)
        return {"access_token": new_access_token, "token_type": "bearer"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

# Add a bookmark (authenticated)
@app.post("/addbookmark")
def add_bookmark(
    bookmark: BookmarkCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # Attach user_id automatically
    bookmark.user_id = current_user.id
    return create_bookmark(db, bookmark)

# Get bookmarks for the authenticated user
@app.get("/getbookmarks")
def get_bookmarks(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return get_user_bookmarks(db, user_id=current_user.id)

# Delete a bookmark (authenticated)
@app.delete("/deletebookmark/{bookmark_id}")
def delete_bookmark(
    bookmark_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # Check if bookmark exists and belongs to the user
    bookmark = get_bookmark_by_id(db, bookmark_id)
    if not bookmark or bookmark.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bookmark not found"
        )
    
    return delete_user_bookmark(db, bookmark_id)


@app.post("/logout")
def logout(refresh_token: str, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    # Delete the refresh token from the DB
    token_entry = db.query(RefreshToken).filter(
        RefreshToken.token == refresh_token,
        RefreshToken.user_id == current_user.id
    ).first()
    
    if token_entry:
        db.delete(token_entry)
        db.commit()

    return {"message": "Logout successful"}
