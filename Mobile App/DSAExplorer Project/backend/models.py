from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "User"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)

    # relationships
    bookmarks = relationship("Bookmarks", back_populates="user", cascade="all, delete")
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete")


class Bookmarks(Base):
    __tablename__ = "Bookmarks"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("User.id", ondelete="CASCADE"))
    algorithm = Column(String, nullable=False)

    # relationship
    user = relationship("User", back_populates="bookmarks")


class RefreshToken(Base):
    __tablename__ = "RefreshToken"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    token = Column(String, unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("User.id", ondelete="CASCADE"))
    created_at = Column(DateTime, default=datetime.utcnow)

    # relationship
    user = relationship("User", back_populates="refresh_tokens")
