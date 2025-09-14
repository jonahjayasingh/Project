from pydantic import BaseModel
from typing import Optional
from datetime import date
import enum

class UserCreate(BaseModel):
    username: str
    password: str


class BookmarkCreate(BaseModel):
    user_id: Optional[int] = None
    algorithm: str
    