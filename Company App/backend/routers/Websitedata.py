import os, json
from uuid import uuid4
from typing import List, Optional
from fastapi import (
    APIRouter, Depends, HTTPException,
    UploadFile, File, Form, status
)
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer

from auth import get_current_user
from models import (
    WebsiteCourse, WebsiteGallery, WebsiteService,
    WebsiteProjectDomain, WebsiteProject,
    WebsitePortfolio, CompanyContacts,
    CompanyCareer, CompanyApplicant, get_db
)
from schema import (
    CompanyCareerCreate,
    CompanyContactsCreate,
    WebsiteCourseResponse,
    WebsiteGalleryResponse,
    WebsiteServiceResponse,
    WebsiteProjectDomainResponse,
    WebsiteProjectResponse,
    WebsitePortfolioResponse,
    CompanyContactsResponse,
    CompanyCareerResponse,
    CompanyApplicantResponse
)

router = APIRouter(prefix="/website", tags=["Website Data"])
course_router = APIRouter(prefix="/courses", tags=["Website Courses"])
gallery_router = APIRouter(prefix="/gallery", tags=["Website Gallery"])
service_router = APIRouter(prefix="/services", tags=["Website Services"])
project_domain_router = APIRouter(prefix="/project-domains", tags=["Website Project Domains"])
project_router = APIRouter(prefix="/projects", tags=["Website Projects"])
portfolio_router = APIRouter(prefix="/portfolios", tags=["Website Portfolios"])
contacts_router = APIRouter(prefix="/contacts", tags=["Company Contacts"])
career_router = APIRouter(prefix="/careers", tags=["Company Careers"])
applicant_router = APIRouter(prefix="/applicants", tags=["Company Applicants"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ============================================================
# Helper functions
# ============================================================
def save_file(file: UploadFile, folder: str) -> Optional[str]:
    if not file:
        return None
    folder_path = os.path.join(UPLOAD_DIR, folder)
    os.makedirs(folder_path, exist_ok=True)
    ext = file.filename.split(".")[-1]
    filename = f"{uuid4()}.{ext}"
    file_path = os.path.join(folder_path, filename)
    with open(file_path, "wb") as f:
        f.write(file.file.read())
    return file_path


def get_object_or_404(model, obj_id: int, db: Session,get_current_user: dict = Depends(get_current_user)):
    obj = db.query(model).filter(model.id == obj_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail=f"{model.__name__} not found")
    return obj


# ============================================================
# WEBSITE COURSES
# ============================================================
@course_router.post("/courses", response_model=WebsiteCourseResponse)
def create_course(
    course_name: str = Form(...),
    course_description: str = Form(""),
    course_price: int = Form(0),
    course_difficulty: str = Form(""),
    course_duration: str = Form(""),
    user_id: int = Form(...),
    course_thumbnail: UploadFile = File(None),
    db: Session = Depends(get_db),
    get_current_user: dict = Depends(get_current_user)
):
    image_path = save_file(course_thumbnail, "courses")
    course = WebsiteCourse(
        course_name=course_name,
        course_description=course_description,
        course_price=course_price,
        course_difficulty=course_difficulty,
        course_duration=course_duration,
        course_thumbnail=image_path,
        user_id=user_id
    )
    db.add(course)
    db.commit()
    db.refresh(course)
    return course


@course_router.get("/courses", response_model=List[WebsiteCourseResponse])
def list_courses(db: Session = Depends(get_db),get_current_user: dict = Depends(get_current_user)):
    return db.query(WebsiteCourse).all()


@course_router.get("/courses/{course_id}", response_model=WebsiteCourseResponse)
def get_course(course_id: int, db: Session = Depends(get_db),get_current_user: dict = Depends(get_current_user)):
    return get_object_or_404(WebsiteCourse, course_id, db)


@course_router.put("/courses/{course_id}", response_model=WebsiteCourseResponse)
def update_course(
    course_id: int,
    course_name: str = Form(None),
    course_description: str = Form(None),
    course_price: int = Form(None),
    course_difficulty: str = Form(None),
    course_duration: str = Form(None),
    user_id: int = Form(None),
    course_thumbnail: UploadFile = File(None),
    db: Session = Depends(get_db)
,get_current_user: dict = Depends(get_current_user)):
    course = get_object_or_404(WebsiteCourse, course_id, db)
    if course_name: course.course_name = course_name
    if course_description: course.course_description = course_description
    if course_price: course.course_price = course_price
    if course_difficulty: course.course_difficulty = course_difficulty
    if course_duration: course.course_duration = course_duration
    if user_id: course.user_id = user_id
    if course_thumbnail:
        course.course_thumbnail = save_file(course_thumbnail, "courses")
    db.commit()
    db.refresh(course)
    return course


@course_router.delete("/courses/{course_id}")
def delete_course(course_id: int, db: Session = Depends(get_db),get_current_user: dict = Depends(get_current_user)):
    course = get_object_or_404(WebsiteCourse, course_id, db)
    db.delete(course)
    db.commit()
    return {"message": "Course deleted successfully"}


# ============================================================
# WEBSITE GALLERY
# ============================================================
@gallery_router.post("/gallery", response_model=WebsiteGalleryResponse)
def create_gallery(
    gallery_title: str = Form(...),
    user_id: int = Form(...),
    gallery_image: UploadFile = File(None),
    db: Session = Depends(get_db)
,get_current_user: dict = Depends(get_current_user)):
    image_path = save_file(gallery_image, "gallery")
    gallery = WebsiteGallery(
        gallery_title=gallery_title,
        gallery_image=image_path,
        user_id=user_id
    )
    db.add(gallery)
    db.commit()
    db.refresh(gallery)
    return gallery


@gallery_router.get("/gallery", response_model=List[WebsiteGalleryResponse])
def list_gallery(db: Session = Depends(get_db),get_current_user: dict = Depends(get_current_user)):
    return db.query(WebsiteGallery).all()


@gallery_router.put("/gallery/{gallery_id}", response_model=WebsiteGalleryResponse)
def update_gallery(
    gallery_id: int,
    gallery_title: str = Form(None),
    gallery_image: UploadFile = File(None),
    db: Session = Depends(get_db)
,get_current_user: dict = Depends(get_current_user)):
    gallery = get_object_or_404(WebsiteGallery, gallery_id, db)
    if gallery_title:
        gallery.gallery_title = gallery_title
    if gallery_image:
        gallery.gallery_image = save_file(gallery_image, "gallery")
    db.commit()
    db.refresh(gallery)
    return gallery


@gallery_router.delete("/gallery/{gallery_id}")
def delete_gallery(gallery_id: int, db: Session = Depends(get_db),get_current_user: dict = Depends(get_current_user)):
    gallery = get_object_or_404(WebsiteGallery, gallery_id, db)
    db.delete(gallery)
    db.commit()
    return {"message": "Gallery deleted successfully"}


# ============================================================
# WEBSITE SERVICES
# ============================================================

@service_router.post("/services", response_model=WebsiteServiceResponse)
def create_service(
    name: str = Form(...),
    description: str = Form(...),
    key_points: str = Form("[]"),
    user_id: int = Form(...),
    image: UploadFile = File(None),
    db: Session = Depends(get_db)
,get_current_user: dict = Depends(get_current_user)):
    image_path = save_file(image, "services")

    try:
        key_points_parsed = json.loads(key_points)
    except Exception:
        key_points_parsed = []

    service = WebsiteService(
        name=name,
        description=description,
        key_points=key_points_parsed,
        image=image_path,
        user_id=user_id
    )
    db.add(service)
    db.commit()
    db.refresh(service)
    return service


@service_router.get("/services", response_model=List[WebsiteServiceResponse])
def list_services(db: Session = Depends(get_db),get_current_user: dict = Depends(get_current_user)):
    return db.query(WebsiteService).all()


@service_router.put("/services/{service_id}", response_model=WebsiteServiceResponse)
def update_service(
    service_id: int,
    name: str = Form(None),
    description: str = Form(None),
    key_points: str = Form(None),
    user_id: int = Form(None),
    image: UploadFile = File(None),
    db: Session = Depends(get_db)
,get_current_user: dict = Depends(get_current_user)):
    service = get_object_or_404(WebsiteService, service_id, db)
    if name: service.name = name
    if description: service.description = description
    if key_points: service.key_points = key_points
    if user_id: service.user_id = user_id
    if image:
        service.image = save_file(image, "services")
    db.commit()
    db.refresh(service)
    return service


@service_router.delete("/services/{service_id}")
def delete_service(service_id: int, db: Session = Depends(get_db),get_current_user: dict = Depends(get_current_user)):
    service = get_object_or_404(WebsiteService, service_id, db)
    db.delete(service)
    db.commit()
    return {"message": "Service deleted successfully"}


# ============================================================
# WEBSITE PROJECT DOMAINS & PROJECTS
# ============================================================

@project_domain_router.post("/domains", response_model=WebsiteProjectDomainResponse)
def create_domain(
    name: str = Form(...),
    description: str = Form(""),
    user_id: int = Form(...),
    image: UploadFile = File(None),
    db: Session = Depends(get_db)
,get_current_user: dict = Depends(get_current_user)):
    image_path = save_file(image, "domains")
    domain = WebsiteProjectDomain(name=name, description=description, image=image_path, user_id=user_id)
    db.add(domain)
    db.commit()
    db.refresh(domain)
    return domain


@project_domain_router.get("/domains", response_model=List[WebsiteProjectDomainResponse])
def list_domains(db: Session = Depends(get_db),get_current_user: dict = Depends(get_current_user)):
    return db.query(WebsiteProjectDomain).all()


@project_domain_router.put("/domains/{domain_id}", response_model=WebsiteProjectDomainResponse)
def update_domain(
    domain_id: int,
    name: str = Form(None),
    description: str = Form(None),
    user_id: int = Form(None),
    image: UploadFile = File(None),
    db: Session = Depends(get_db)
,get_current_user: dict = Depends(get_current_user)):
    domain = get_object_or_404(WebsiteProjectDomain, domain_id, db)
    if name: domain.name = name
    if description: domain.description = description
    if user_id: domain.user_id = user_id
    if image:
        domain.image = save_file(image, "domains")
    db.commit()
    db.refresh(domain)
    return domain


@project_domain_router.delete("/domains/{domain_id}")
def delete_domain(domain_id: int, db: Session = Depends(get_db),get_current_user: dict = Depends(get_current_user)):
    domain = get_object_or_404(WebsiteProjectDomain, domain_id, db)
    db.delete(domain)
    db.commit()
    return {"message": "Domain deleted successfully"}


@project_router.post("/domains/{domain_id}/projects", response_model=WebsiteProjectResponse)
def create_project(domain_id: int, project_data: WebsiteProjectResponse, db: Session = Depends(get_db),get_current_user: dict = Depends(get_current_user)):
    domain = get_object_or_404(WebsiteProjectDomain, domain_id, db)
    project = WebsiteProject(**project_data.dict(), domain_id=domain.id)
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@project_router.get("/projects", response_model=List[WebsiteProjectResponse])
def list_projects(db: Session = Depends(get_db),get_current_user: dict = Depends(get_current_user)):
    return db.query(WebsiteProject).all()


@project_router.delete("/projects/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db),get_current_user: dict = Depends(get_current_user)):
    project = get_object_or_404(WebsiteProject, project_id, db)
    db.delete(project)
    db.commit()
    return {"message": "Project deleted successfully"}





# ============================================================
# WEBSITE PORTFOLIO
# ============================================================
@portfolio_router.post("/portfolio", response_model=WebsitePortfolioResponse)
def create_portfolio(
    title: str = Form(...),
    description: str = Form(""),
    project_type: str = Form(""),
    project_url: str = Form(""),
    user_id: int = Form(...),
    project_image: UploadFile = File(None),
    db: Session = Depends(get_db)
,get_current_user: dict = Depends(get_current_user)):
    image_path = save_file(project_image, "portfolio")
    portfolio = WebsitePortfolio(
        title=title,
        description=description,
        project_type=project_type,
        project_url=project_url,
        user_id=user_id,
        project_image=image_path
    )
    db.add(portfolio)
    db.commit()
    db.refresh(portfolio)
    return portfolio


@portfolio_router.get("/portfolio", response_model=List[WebsitePortfolioResponse])
def list_portfolio(db: Session = Depends(get_db),get_current_user: dict = Depends(get_current_user)):
    return db.query(WebsitePortfolio).all()


@portfolio_router.put("/portfolio/{portfolio_id}", response_model=WebsitePortfolioResponse)
def update_portfolio(
    portfolio_id: int,
    title: str = Form(None),
    description: str = Form(None),
    project_type: str = Form(None),
    project_url: str = Form(None),
    user_id: int = Form(None),
    project_image: UploadFile = File(None),
    db: Session = Depends(get_db)
,get_current_user: dict = Depends(get_current_user)):
    portfolio = get_object_or_404(WebsitePortfolio, portfolio_id, db)
    if title: portfolio.title = title
    if description: portfolio.description = description
    if project_type: portfolio.project_type = project_type
    if project_url: portfolio.project_url = project_url
    if user_id: portfolio.user_id = user_id
    if project_image:
        portfolio.project_image = save_file(project_image, "portfolio")
    db.commit()
    db.refresh(portfolio)
    return portfolio


@portfolio_router.delete("/portfolio/{portfolio_id}")
def delete_portfolio(portfolio_id: int, db: Session = Depends(get_db),get_current_user: dict = Depends(get_current_user)):
    portfolio = get_object_or_404(WebsitePortfolio, portfolio_id, db)
    db.delete(portfolio)
    db.commit()
    return {"message": "Portfolio deleted successfully"}


# ============================================================
# COMPANY CONTACTS
# ============================================================
@contacts_router.post("/contacts", response_model=CompanyContactsResponse)
def create_contact(data: CompanyContactsCreate, db: Session = Depends(get_db),get_current_user: dict = Depends(get_current_user)):
    contact = CompanyContacts(**data.dict())
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact




@contacts_router.get("/contacts", response_model=List[CompanyContactsResponse])
def list_contacts(db: Session = Depends(get_db),get_current_user: dict = Depends(get_current_user)):
    return db.query(CompanyContacts).all()


@contacts_router.delete("/contacts/{contact_id}")
def delete_contact(contact_id: int, db: Session = Depends(get_db),get_current_user: dict = Depends(get_current_user)):
    contact = get_object_or_404(CompanyContacts, contact_id, db)
    db.delete(contact)
    db.commit()
    return {"message": "Contact deleted successfully"}


# ============================================================
# COMPANY CAREERS + APPLICANTS
# ============================================================
@career_router.post("/careers", response_model=CompanyCareerResponse)
def create_career(data: CompanyCareerCreate, db: Session = Depends(get_db),get_current_user: dict = Depends(get_current_user)):
    career = CompanyCareer(**data.dict())
    db.add(career)
    db.commit()
    db.refresh(career)
    return career



@applicant_router.get("/careers", response_model=List[CompanyCareerResponse])
def list_careers(db: Session = Depends(get_db),get_current_user: dict = Depends(get_current_user)):
    return db.query(CompanyCareer).all()


@applicant_router.delete("/careers/{career_id}")
def delete_career(career_id: int, db: Session = Depends(get_db),get_current_user: dict = Depends(get_current_user)):
    career = get_object_or_404(CompanyCareer, career_id, db)
    db.delete(career)
    db.commit()
    return {"message": "Career deleted successfully"}


@applicant_router.post("/careers/{career_id}/apply", response_model=CompanyApplicantResponse)
def apply_job(
    career_id: int,
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: str = Form(...),
    phone: int = Form(...),
    experience: str = Form(""),
    current_company: str = Form(""),
    cover_letter: str = Form(""),
    resume: UploadFile = File(...),
    db: Session = Depends(get_db)
,get_current_user: dict = Depends(get_current_user)):
    career = get_object_or_404(CompanyCareer, career_id, db)
    resume_path = save_file(resume, "resumes")
    applicant = CompanyApplicant(
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone=phone,
        experience=experience,
        current_company=current_company,
        cover_letter=cover_letter,
        career_id=career.id,
        resume_path=resume_path
    )
    db.add(applicant)
    db.commit()
    db.refresh(applicant)
    return applicant


@applicant_router.get("/applicants", response_model=List[CompanyApplicantResponse])
def list_applicants(db: Session = Depends(get_db),get_current_user: dict = Depends(get_current_user)):
    return db.query(CompanyApplicant).all()


@applicant_router.delete("/applicants/{applicant_id}")
def delete_applicant(applicant_id: int, db: Session = Depends(get_db),get_current_user: dict = Depends(get_current_user)):
    applicant = get_object_or_404(CompanyApplicant, applicant_id, db)
    db.delete(applicant)
    db.commit()
    return {"message": "Applicant deleted successfully"}



router.include_router(course_router)
router.include_router(applicant_router)
router.include_router(project_router)
router.include_router(contacts_router)
router.include_router(career_router)
router.include_router(project_domain_router)
router.include_router(portfolio_router)
router.include_router(service_router)
router.include_router(gallery_router)


