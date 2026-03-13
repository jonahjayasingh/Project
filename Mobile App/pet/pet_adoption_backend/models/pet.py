from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from database.db import Base
import datetime

class Pet(Base):
    __tablename__ = "pets"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String)
    breed = Column(String)
    age = Column(String)
    gender = Column(String)
    category = Column(String)
    description = Column(String)
    location = Column(String)
    latitude = Column(Float, nullable=True) # Adding for geolocator logic
    longitude = Column(Float, nullable=True)
    is_featured = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    owner = relationship("User", back_populates="pets")
    media = relationship("PetMedia", back_populates="pet", cascade="all, delete-orphan")

class PetMedia(Base):
    __tablename__ = "pet_media"

    id = Column(Integer, primary_key=True, index=True)
    pet_id = Column(Integer, ForeignKey("pets.id"))
    file_type = Column(String) # image or video
    file_url = Column(String)

    pet = relationship("Pet", back_populates="media")
