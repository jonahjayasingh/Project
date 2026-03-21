from pydantic import BaseModel, EmailStr
from typing import Optional, List

class UserBase(BaseModel):
    name: str
    email: EmailStr
    phone: str
    location: str
<<<<<<< HEAD
=======
    profile_image: Optional[str] = None
>>>>>>> fac2c57 (add)

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    location: Optional[str] = None
<<<<<<< HEAD
=======
    profile_image: Optional[str] = None
>>>>>>> fac2c57 (add)
    password: Optional[str] = None

class UserOut(UserBase):
    id: int
    is_admin: bool

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
