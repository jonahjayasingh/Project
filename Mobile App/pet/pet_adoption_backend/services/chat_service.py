from sqlalchemy.orm import Session
<<<<<<< HEAD
=======
from sqlalchemy import or_
>>>>>>> fac2c57 (add)
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
<<<<<<< HEAD
    return db.query(Message).filter(Message.pet_id == chat_id).order_by(Message.created_at.asc()).all()
=======
    return db.query(Message).filter(Message.pet_id == chat_id).order_by(Message.created_at.desc()).all()

def get_inbox_messages(db: Session, user_id: int):
    messages = db.query(Message).filter(
        or_(Message.sender_id == user_id, Message.receiver_id == user_id)
    ).order_by(Message.created_at.desc()).all()
    
    inbox = []
    seen_pets = set()
    for msg in messages:
        if msg.pet_id not in seen_pets:
            seen_pets.add(msg.pet_id)
            
            pet_name = msg.pet.name if msg.pet else "Unknown Pet"
            pet_media = msg.pet.media[0].file_url if (msg.pet and msg.pet.media and len(msg.pet.media) > 0) else None
            
            partner = msg.receiver if msg.sender_id == user_id else msg.sender
            partner_name = partner.name if partner else "Unknown User"
            
            inbox.append({
                "id": msg.id,
                "pet_id": msg.pet_id,
                "pet_name": pet_name,
                "pet_media": pet_media,
                "partner_name": partner_name,
                "last_message": msg.message,
                "created_at": msg.created_at,
                "sender_id": msg.sender_id,
                "receiver_id": msg.receiver_id
            })
    return inbox
>>>>>>> fac2c57 (add)
