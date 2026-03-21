from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class PetMediaBase(BaseModel):
    file_type: str
    file_url: str

class PetMediaOut(PetMediaBase):
    id: int
    pet_id: int

    class Config:
        orm_mode = True

class PetBase(BaseModel):
    name: str
    breed: str
    age: str
    gender: str
    category: str
    description: str
    location: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class PetCreate(PetBase):
    pass

class PetUpdate(BaseModel):
    name: Optional[str] = None
    breed: Optional[str] = None
    age: Optional[str] = None
    gender: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    is_featured: Optional[bool] = None

class PetOut(PetBase):
    id: int
    owner_id: int
<<<<<<< HEAD
=======
    owner_phone: Optional[str] = None
    owner_name: Optional[str] = None
>>>>>>> fac2c57 (add)
    is_featured: bool
    created_at: datetime
    media: List[PetMediaOut] = []

    class Config:
        orm_mode = True
