from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import date, datetime


class UserBase(BaseModel):
    username: str
    email: EmailStr
    phone : int
    password: str
    

class UserCreate(UserBase):
    password: str
    is_admin: Optional[bool] = None
    is_staff : Optional[bool] = None
    is_student : Optional[bool] = None
    


class UserLogin(BaseModel):
    username: str
    password: str

# ============================================================
# WEBSITE COURSE
# ============================================================
class WebsiteCourseBase(BaseModel):
    course_name: str
    course_description: Optional[str] = None
    course_price: Optional[int] = None
    course_thumbnail: Optional[str] = None  # URL or path to uploaded file
    course_difficulty: Optional[str] = None
    course_duration: Optional[str] = None
    user_id: Optional[int] = None


class WebsiteCourseCreate(WebsiteCourseBase):
    pass


class WebsiteCourseResponse(WebsiteCourseBase):
    id: int

    class Config:
        orm_mode = True


# ============================================================
# WEBSITE GALLERY
# ============================================================
class WebsiteGalleryBase(BaseModel):
    gallery_title: str
    gallery_image: Optional[str] = None
    user_id: Optional[int] = None


class WebsiteGalleryCreate(WebsiteGalleryBase):
    pass


class WebsiteGalleryResponse(WebsiteGalleryBase):
    id: int

    class Config:
        orm_mode = True


# ============================================================
# WEBSITE SERVICES
# ============================================================
class WebsiteServiceBase(BaseModel):
    name: str
    description: str
    image: Optional[str] = None
    key_points: Optional[List[str]] = None
    user_id: Optional[int] = None


class WebsiteServiceCreate(WebsiteServiceBase):
    pass


class WebsiteServiceResponse(WebsiteServiceBase):
    id: int

    class Config:
        orm_mode = True


# ============================================================
# WEBSITE PROJECT DOMAIN & PROJECT
# ============================================================
class WebsiteProjectDomainBase(BaseModel):
    name: str
    description: Optional[str] = None
    image: Optional[str] = None
    user_id: Optional[int] = None


class WebsiteProjectDomainCreate(WebsiteProjectDomainBase):
    pass


class WebsiteProjectDomainResponse(WebsiteProjectDomainBase):
    id: int

    class Config:
        orm_mode = True


class WebsiteProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    domain_id: Optional[int] = None


class WebsiteProjectCreate(WebsiteProjectBase):
    pass


class WebsiteProjectResponse(WebsiteProjectBase):
    id: int

    class Config:
        orm_mode = True


# ============================================================
# WEBSITE PORTFOLIO
# ============================================================
class WebsitePortfolioBase(BaseModel):
    title: str
    description: Optional[str] = None
    project_image: Optional[str] = None
    technologies_used: Optional[List[str]] = None
    project_type: Optional[str] = None
    project_url: Optional[str] = None
    user_id: Optional[int] = None


class WebsitePortfolioCreate(WebsitePortfolioBase):
    pass


class WebsitePortfolioResponse(WebsitePortfolioBase):
    id: int

    class Config:
        orm_mode = True


# ============================================================
# COMPANY CONTACTS
# ============================================================
class CompanyContactsBase(BaseModel):
    phone1: int
    phone2: Optional[int] = None
    email: EmailStr
    whatsapp: Optional[int] = None
    address: Optional[str] = None
    linkedin: Optional[str] = None
    twitter: Optional[str] = None
    facebook: Optional[str] = None
    instagram: Optional[str] = None
    youtube: Optional[str] = None
    map_embed_url: Optional[str] = None
    user_id: Optional[int] = None


class CompanyContactsCreate(CompanyContactsBase):
    pass


class CompanyContactsResponse(CompanyContactsBase):
    id: int

    class Config:
        orm_mode = True


# ============================================================
# COMPANY CAREER + APPLICANT
# ============================================================
class CompanyCareerBase(BaseModel):
    title: str
    description: Optional[str] = None
    location: Optional[str] = None
    application_deadline: Optional[date] = None
    job_type: Optional[str] = None
    experience: Optional[str] = None
    key_responsibilities: Optional[List[str]] = None
    user_id: Optional[int] = None


class CompanyCareerCreate(CompanyCareerBase):
    pass


class CompanyCareerResponse(CompanyCareerBase):
    id: int

    class Config:
        orm_mode = True


class CompanyApplicantBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: int
    experience: Optional[str] = None
    current_company: Optional[str] = None
    resume_path: Optional[str] = None
    cover_letter: Optional[str] = None
    career_id: Optional[int] = None


class CompanyApplicantCreate(CompanyApplicantBase):
    pass


class CompanyApplicantResponse(CompanyApplicantBase):
    id: int

    class Config:
        orm_mode = True
