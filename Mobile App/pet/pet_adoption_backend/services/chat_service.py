from sqlalchemy.orm import Session
from models.message import Message
from schemas.message_schema import MessageCreate

def send_message(db: Session, message: MessageCreate, sender_id: int):
    # In a real app, you might want to find the receiver from the pet_id
    from models.pet import Pet
    pet = db.query(Pet).filter(Pet.id == message.pet_id).first()
    if not pet:
        return None
    
    db_message = Message(
        sender_id=sender_id,
        receiver_id=pet.owner_id,
        pet_id=message.pet_id,
        message=message.message
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

def get_chat_messages(db: Session, chat_id: int, user_id: int):
    # Simplification: chat_id could be a composite of user IDs or just filter by pet/users
    # Here we'll just return messages related to a specific pet between two users
    return db.query(Message).filter(Message.pet_id == chat_id).order_by(Message.created_at.asc()).all()
