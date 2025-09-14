from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import Base, engine
from models import User, RefreshToken, Bookmarks
from crud import get_db, create_user, create_bookmark, get_user_bookmarks, delete_user_bookmark, get_bookmark_by_id
from auth import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    get_current_user,
    decode_token
)


# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------
# Pydantic Schemas
# -------------------------
class UserCreate(BaseModel):
    username: str
    password: str

class BookmarkCreate(BaseModel):
    algorithm_id: str
    user_id: int = None  # will attach automatically

class TokenRefreshRequest(BaseModel):
    refresh_token: str

# -------------------------
# Routes
# -------------------------
@app.get("/")
def home():
    return {"greeting": "Hello"}

# -------------------------
# User Registration
# -------------------------
@app.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with that name already exists"
        )
    user.password = hash_password(user.password)
    return create_user(db, user)

# -------------------------
# Login
# -------------------------
@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == form_data.username).first()
    if not db_user or not verify_password(form_data.password, db_user.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": db_user.username})
    refresh_token = create_refresh_token(data={"sub": db_user.username})

    # Save refresh token in DB
    db_refresh = RefreshToken(token=refresh_token, user_id=db_user.id)
    db.add(db_refresh)
    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "username": db_user.username
    }

# -------------------------
# Refresh Token
# -------------------------
@app.post("/refresh")
def refresh_access_token(request: TokenRefreshRequest, db: Session = Depends(get_db)):
    username = decode_token(request.refresh_token, scope="refresh_token")
    token_entry = db.query(RefreshToken).filter(RefreshToken.token == request.refresh_token).first()

    if not username or not token_entry:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    return {"access_token": create_access_token(data={"sub": username}), "token_type": "bearer"}

# -------------------------
# Logout
# -------------------------
@app.post("/logout")
def logout(request: TokenRefreshRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    token_entry = db.query(RefreshToken).filter(
        RefreshToken.token == request.refresh_token,
        RefreshToken.user_id == current_user.id
    ).first()
    
    if token_entry:
        db.delete(token_entry)
        db.commit()

    return {"message": "Logout successful"}

# -------------------------
# Bookmarks
@app.post("/addbookmark")
def add_bookmark(
    bookmark_data: BookmarkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        existing = db.query(Bookmarks).filter(
            Bookmarks.user_id == current_user.id,
            Bookmarks.algorithm_id == bookmark_data.algorithm_id
        ).first()

        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bookmark already exists")

        bookmark_data.user_id = current_user.id

        return create_bookmark(db, bookmark_data)
    except Exception as e:
        import traceback
        print("Add Bookmark Error:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/getbookmarks")
def get_bookmarks(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_user_bookmarks(db, user_id=current_user.id)

@app.get("/checkbookmark/{bookmark_id}")
def checkbookmark(
    bookmark_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    bookmark = get_bookmark_by_id(db, bookmark_id)
    is_bookmarked = bookmark is not None and bookmark.user_id == current_user.id
    return {"is_bookmarked": is_bookmarked}


@app.delete("/deletebookmark/{bookmark_id}")
def delete_bookmark(bookmark_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    bookmark = get_bookmark_by_id(db, bookmark_id)
    if not bookmark or bookmark.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bookmark not found")
    
    return delete_user_bookmark(db, bookmark_id)
