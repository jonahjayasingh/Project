from sqlalchemy import create_engine, Column, Integer, String, Date, Time, LargeBinary, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

# Create a new SQLite database
engine = create_engine('sqlite:///information.db')
Base = declarative_base()

# Admin model
class Admin(Base):
    __tablename__ = 'admins'
    id = Column(Integer, primary_key=True)
    username = Column(String(150), nullable=False, unique=True)
    password = Column(String(150), nullable=False)

# Student Data model
class StudentData(Base):
    __tablename__ = "studentdata"
    registration_id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False)
    image = Column(String(500), nullable=False)
    
    # Relationship to attendance records
    attendances = relationship("Attendance", back_populates="student", cascade="all, delete-orphan")

# Attendance model
class Attendance(Base):
    __tablename__ = 'attendances'
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('studentdata.registration_id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    Date = Column(Date, default=datetime.today)
    Time = Column(Time, default=datetime.now().time)
    
    # Relationship to student
    student = relationship("StudentData", back_populates="attendances")
    
    # Property to get student name (for backward compatibility)
    @property
    def Name(self):
        return self.student.name if self.student else "Unknown"

# Create tables in the database
Base.metadata.create_all(engine)

# Create a session factory
Session = sessionmaker(bind=engine)

def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()

print("Database and tables created successfully!")
