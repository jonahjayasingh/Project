from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class MessageBase(BaseModel):
    receiver_id: int
    pet_id: int
    message: str

class MessageCreate(MessageBase):
    pass

class MessageOut(MessageBase):
    id: int
    sender_id: int
    created_at: datetime

    class Config:
        orm_mode = True
