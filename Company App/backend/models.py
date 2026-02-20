from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    DateTime,
    Date,
    Numeric,
    Boolean,
    ForeignKey,
    BigInteger,
    Text,
    JSON,
)
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from datetime import datetime, date
import os
from sqlalchemy import event

# --------------------------------------------------------
# Database setup
# --------------------------------------------------------
engine = create_engine("sqlite:///./database.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# --------------------------------------------------------
# User model
# --------------------------------------------------------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String, index=True)
    password = Column(String)
    email = Column(String, unique=True, index=True, default=None, nullable=True)
    phone = Column(Numeric, unique=True, index=True, default=None)
    is_admin = Column(Boolean, default=False)
    is_staff = Column(Boolean, default=False)
    is_student = Column(Boolean, default=False)
    last_login = Column(DateTime, default=None)
    created_at = Column(DateTime, default=datetime.now)

    # relationships
    staff_permissions = relationship("StaffPermission", back_populates="user", cascade="all, delete-orphan")
    students = relationship("Student", foreign_keys="[Student.user_id]", back_populates="user")
    faculty_students = relationship("Student", foreign_keys="[Student.faculty_id]", back_populates="faculty")
    works = relationship("Work", back_populates="user", cascade="all, delete-orphan")
    attendance = relationship("Attendance", back_populates="user", cascade="all, delete-orphan")
    website_courses = relationship("WebsiteCourse", back_populates="user", cascade="all, delete-orphan")
    website_gallery = relationship("WebsiteGallery", back_populates="user", cascade="all, delete-orphan")
    website_services = relationship("WebsiteService", back_populates="user", cascade="all, delete-orphan")
    website_domains = relationship("WebsiteProjectDomain", back_populates="user", cascade="all, delete-orphan")
    website_portfolios = relationship("WebsitePortfolio", back_populates="user", cascade="all, delete-orphan")
    company_contacts = relationship("CompanyContacts", back_populates="user", cascade="all, delete-orphan")
    company_careers = relationship("CompanyCareer", back_populates="user", cascade="all, delete-orphan")


# --------------------------------------------------------
# Student + academic system
# --------------------------------------------------------
class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, index=True)
    address = Column(String, index=True)
    duration = Column(String, default="0")
    total_payment = Column(Numeric, default=0)
    payment_status = Column(Boolean, default=False)
    dob = Column(Date, default=None)
    joined_at = Column(Date, nullable=True)
    pincode = Column(Integer, default=None)
    qualification = Column(String, index=True)
    marital_status = Column(String, index=True)
    is_online = Column(Boolean, default=False)
    is_completed = Column(Boolean, default=False)
    project_title = Column(String, index=True, nullable=True)
    date_range = Column(String, index=True, nullable=True)
    completed_date = Column(Date, nullable=True)
    certificate_type = Column(String, index=True, nullable=True)
    certificate_id = Column(String, nullable=True)

    faculty_id = Column(Integer, ForeignKey("users.id"), default=None)
    user_id = Column(Integer, ForeignKey("users.id"), default=None)

    user = relationship("User", foreign_keys=[user_id], back_populates="students")
    faculty = relationship("User", foreign_keys=[faculty_id], back_populates="faculty_students")
    attendance = relationship("Attendance", back_populates="student", cascade="all, delete-orphan")


class StaffPermission(Base):
    __tablename__ = "staffpermissions"

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    receipt_permission = Column(Boolean, default=False)
    certificate_permission = Column(Boolean, default=False)
    add_student_permission = Column(Boolean, default=False)

    user_id = Column(Integer, ForeignKey("users.id"), default=None)
    user = relationship("User", back_populates="staff_permissions")


# --------------------------------------------------------
# Administrative models
# --------------------------------------------------------
class Course(Base):
    __tablename__ = "courses"
    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    course_name = Column(String, unique=True)


class Receipt(Base):
    __tablename__ = "receipts"
    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    amount = Column(Integer)
    date = Column(Date, default=date.today)
    reg_no = Column(Integer)
    student_id = Column(Integer, ForeignKey("students.id"), default=None)
    course_id = Column(Integer, ForeignKey("courses.id"), default=None)
    user_id = Column(Integer, ForeignKey("users.id"), default=None)


class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    paid_amount = Column(Integer, default=0)
    user_id = Column(Integer, ForeignKey("users.id"), default=None)


class Account(Base):
    __tablename__ = "accounts"
    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    balance = Column(Integer, default=0)
    user_id = Column(Integer, ForeignKey("users.id"), default=None)


class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    transaction_type = Column(String)
    description = Column(String)
    timestamp = Column(DateTime, default=datetime.now)
    amount = Column(Integer)
    account_id = Column(Integer, ForeignKey("accounts.id"), default=None)


# --------------------------------------------------------
# Staff and Work tracking
# --------------------------------------------------------
class StaffDetails(Base):
    __tablename__ = "staffdetails"

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    photo = Column(String)
    name = Column(String)
    address = Column(String)
    phone = Column(BigInteger)
    email = Column(String)
    pincode = Column(Integer)
    designation = Column(String)
    joining_date = Column(Date)
    dob = Column(Date)
    salary = Column(Integer)
    employee_id = Column(Integer)
    resignation_date = Column(Date, nullable=True)
    documents = Column(Text)

    user_id = Column(Integer, ForeignKey("users.id"), default=None)


class Work(Base):
    __tablename__ = "works"

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    time_slot = Column(String(100), nullable=False)
    work = Column(Text, nullable=True, default="")
    date = Column(Date, default=date.today)

    user = relationship("User", back_populates="works")


class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(100), nullable=False)
    date = Column(Date, default=date.today)

    user = relationship("User", back_populates="attendance")
    student = relationship("Student", back_populates="attendance")


# --------------------------------------------------------
# Website-related models (CMS)
# --------------------------------------------------------
class WebsiteCourse(Base):
    __tablename__ = "website_courses"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    course_name = Column(String(500))
    course_description = Column(Text)
    course_duration = Column(String(500))
    course_price = Column(Integer)
    course_difficulty = Column(String(500))
    course_thumbnail = Column(String(500))

    user = relationship("User", back_populates="website_courses")


class WebsiteGallery(Base):
    __tablename__ = "website_gallery"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    gallery_title = Column(String(500))
    gallery_image = Column(String(500))

    user = relationship("User", back_populates="website_gallery")


class WebsiteService(Base):
    __tablename__ = "website_services"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    name = Column(String(500))
    description = Column(Text)
    image = Column(String(500))
    key_points = Column(JSON)

    user = relationship("User", back_populates="website_services")


class WebsiteProjectDomain(Base):
    __tablename__ = "website_project_domains"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    name = Column(String(500))
    description = Column(Text)
    image = Column(String(500))

    user = relationship("User", back_populates="website_domains")
    projects = relationship("WebsiteProject", back_populates="domain", cascade="all, delete-orphan")


class WebsiteProject(Base):
    __tablename__ = "website_projects"

    id = Column(Integer, primary_key=True)
    domain_id = Column(Integer, ForeignKey("website_project_domains.id", ondelete="CASCADE"))
    name = Column(String(500))
    description = Column(Text)

    domain = relationship("WebsiteProjectDomain", back_populates="projects")


class WebsitePortfolio(Base):
    __tablename__ = "website_portfolios"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    title = Column(String(500))
    description = Column(Text)
    project_image = Column(String(500))
    technologies_used = Column(JSON)
    project_type = Column(String(500))
    project_url = Column(String(1000))

    user = relationship("User", back_populates="website_portfolios")


class CompanyContacts(Base):
    __tablename__ = "company_contacts"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    phone1 = Column(BigInteger)
    phone2 = Column(BigInteger)
    email = Column(String(255))
    whatsapp = Column(BigInteger)
    address = Column(Text)
    linkedin = Column(String(1000))
    twitter = Column(String(1000))
    facebook = Column(String(1000))
    instagram = Column(String(1000))
    youtube = Column(String(1000))
    map_embed_url = Column(Text)

    user = relationship("User", back_populates="company_contacts")


class CompanyCareer(Base):
    __tablename__ = "company_careers"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    title = Column(String(500))
    description = Column(Text)
    location = Column(String(500))
    application_deadline = Column(Date)
    job_type = Column(String(500))
    experience = Column(String(500))
    key_responsibilities = Column(JSON)

    user = relationship("User", back_populates="company_careers")
    applicants = relationship("CompanyApplicant", back_populates="career", cascade="all, delete-orphan")


class CompanyApplicant(Base):
    __tablename__ = "company_applicants"

    id = Column(Integer, primary_key=True)
    first_name = Column(String(500))
    last_name = Column(String(500))
    email = Column(String(255))
    phone = Column(BigInteger)
    experience = Column(String(500))
    current_company = Column(String(500))
    resume_path = Column(String(1000))
    cover_letter = Column(Text)
    career_id = Column(Integer, ForeignKey("company_careers.id", ondelete="CASCADE"))

    career = relationship("CompanyCareer", back_populates="applicants")

# --------------------------------------------------------
# File cleanup hook for resumes
# --------------------------------------------------------
def _delete_resume_on_delete(mapper, connection, target):
    try:
        path = target.resume_path
        if path and os.path.exists(path):
            os.remove(path)
    except Exception:
        pass


event.listen(CompanyApplicant, "after_delete", _delete_resume_on_delete)


# --------------------------------------------------------
# DB Dependency
# --------------------------------------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

