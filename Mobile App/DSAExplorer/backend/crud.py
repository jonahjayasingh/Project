from sqlalchemy.orm import Session
import models
from models import User
from database import SessionLocal
from fastapi import HTTPException
import schemas

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(username=user.username, password=user.password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"message": f"User {user.username}'s account has been created successfully"}




def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def create_bookmark(db: Session, bookmark: schemas.BookmarkCreate):
    db_bookmark = models.Bookmarks(user_id=bookmark.user_id, algorithm_id=bookmark.algorithm_id)
    db.add(db_bookmark)
    db.commit()
    db.refresh(db_bookmark)
    return {"message": f"Bookmark for user {bookmark.user_id} has been created successfully"}

def get_user_bookmarks(db: Session, user_id: int):
    return db.query(models.Bookmarks).filter(models.Bookmarks.user_id == user_id).all()

def delete_user_bookmark(db: Session, bookmark_id: int):
    db_bookmark = db.query(models.Bookmarks ).filter(models.Bookmarks.id == bookmark_id).first()
    if db_bookmark:
        db.delete(db_bookmark)
        db.commit()
        return {"message": f"Bookmark {bookmark_id} has been deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Bookmark not found")
    
def get_bookmark_by_id(db: Session, bookmark_id: int):
    return db.query(models.Bookmarks).filter(models.Bookmarks.id == bookmark_id).first()