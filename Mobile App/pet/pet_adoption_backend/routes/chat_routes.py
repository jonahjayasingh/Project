from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database.db import get_db
from models.user import User
from schemas.message_schema import MessageCreate, MessageOut
from services.chat_service import send_message, get_chat_messages
from routes.auth_routes import get_current_user

router = APIRouter(prefix="/messages", tags=["messages"])

@router.post("/", response_model=MessageOut)
def post_message(message: MessageCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_message = send_message(db, message, current_user.id)
    if not db_message:
        raise HTTPException(status_code=404, detail="Pet or owner not found")
    return db_message

@router.get("/{chat_id}", response_model=List[MessageOut])
def list_messages(chat_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_chat_messages(db, chat_id, current_user.id)
