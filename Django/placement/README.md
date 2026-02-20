# Placement Management System

A comprehensive Django-based web application designed to streamline and manage the entire placement process for educational institutions. This system facilitates seamless interaction between students, teachers/placement officers, companies, and administrators.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [System Architecture](#system-architecture)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [User Roles](#user-roles)
- [Project Structure](#project-structure)
- [Database Models](#database-models)
- [Contributing](#contributing)
- [License](#license)

## 🎯 Overview

The Placement Management System is a full-featured web application that automates and manages the campus placement process. It provides role-based access control for different stakeholders including students, teachers, companies, and administrators, enabling efficient management of job postings, applications, student profiles, training sessions, and placement reports.

## ✨ Features

### 🎓 Student Module

- **Profile Management**
  - Complete student profile with personal details
  - Academic information (course, branch, year, semester, roll number, registration number)
  - CGPA tracking and calculation
  - Resume upload and approval workflow
  - Profile picture management

- **Job Portal**
  - Browse available job postings
  - Filter jobs based on eligibility (CGPA threshold)
  - Apply for jobs with cover letters
  - Track application status
  - View job details (salary, location, type, mode)

- **Training & Development**
  - Access training sessions created by placement faculty
  - View recorded training videos
  - Join live Google Meet sessions
  - Access quiz links for skill assessment

- **Dashboard**
  - Personalized student dashboard
  - View notifications
  - Track placement statistics
  - Alumni information

### 👨‍🏫 Teacher/Placement Officer Module

- **Profile Management**
  - Teacher profile with designation and specialization
  - Department assignment
  - HOD and Placement Faculty role designation

- **Student Management**
  - View all registered students
  - Filter students by course, branch, year
  - Approve/reject student resumes
  - View student CGPA and placement status
  - Access student profiles and contact information

- **Training Management**
  - Create and schedule training sessions
  - Upload training videos
  - Add Google Meet links for live sessions
  - Share quiz/assessment links (Google Forms integration)
  - Edit and delete training sessions

- **Alumni Management**
  - View and manage alumni records
  - Track alumni job placements
  - Alumni statistics and reports

- **Notifications**
  - Send notifications to students
  - Track notification status

### 🏢 Company Module

- **Company Profile**
  - Company details (name, location, industry type)
  - Contact information
  - Profile picture/logo

- **Job Posting**
  - Create job postings with detailed descriptions
  - Set CGPA thresholds for eligibility
  - Specify job type (Full-time, Internship, etc.)
  - Set job mode (On-site, Remote, Hybrid)
  - Manage active/inactive job status

- **Application Management**
  - View all applications for posted jobs
  - Filter applications by criteria
  - Access student profiles and resumes

### 🔐 Principal/Admin Module

- **User Approval System**
  - Approve/reject new user registrations
  - Assign user roles (Student, Teacher, Company)
  - Manage user permissions

- **Degree & Specialization Management**
  - Add/edit/delete degree programs
  - Manage specializations
  - Configure academic programs

- **Reports & Analytics**
  - Comprehensive placement reports
  - Year-wise placement statistics
  - Branch-wise analysis
  - Company-wise placement data
  - CGPA-based analytics
  - Export reports

- **System-wide Notifications**
  - Broadcast notifications to all users
  - Targeted notifications by role

### 📊 Common Features

- **Authentication & Authorization**
  - Secure user registration and login
  - Role-based access control
  - Password validation
  - Session management

- **Notification System**
  - Real-time notifications
  - Read/unread status tracking
  - Clear notifications functionality

- **Responsive Design**
  - Mobile-friendly interface
  - Modern UI/UX
  - Accessible across devices

## 🛠️ Technology Stack

### Backend
- **Framework**: Django 5.2.4
- **Language**: Python 3.x
- **Database**: SQLite3 (Development)
- **ORM**: Django ORM

### Frontend
- **HTML5**
- **CSS3**
- **JavaScript**
- **Bootstrap** (for responsive design)

### Additional Technologies
- **File Upload**: Django File Handling
- **Image Processing**: PIL/Pillow
- **Authentication**: Django Auth System
- **Media Storage**: Local file system

## 🏗️ System Architecture

The application follows Django's MVT (Model-View-Template) architecture:

```
┌─────────────┐
│   Browser   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   URLs      │ (Routing)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Views     │ (Business Logic)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Models    │ (Data Layer)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Database   │ (SQLite3)
└─────────────┘
```

### Application Modules

1. **app** - Core application (authentication, dashboard, principal functions)
2. **student** - Student-specific features
3. **teacher** - Teacher/placement officer features
4. **company** - Company/recruiter features

## 📦 Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### Step-by-Step Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd placement
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```

4. **Install dependencies**
   ```bash
   pip install django pillow
   ```

5. **Navigate to the project directory**
   ```bash
   cd placement
   ```

6. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

7. **Create a superuser (admin)**
   ```bash
   python manage.py createsuperuser
   ```

8. **Collect static files**
   ```bash
   python manage.py collectstatic
   ```

9. **Run the development server**
   ```bash
   python manage.py runserver
   ```

10. **Access the application**
    - Open your browser and navigate to: `http://127.0.0.1:8000/`
    - Admin panel: `http://127.0.0.1:8000/admin/`

## ⚙️ Configuration

### Settings Configuration

The main settings file is located at `placement/placement/settings.py`. Key configurations include:

- **SECRET_KEY**: Change this in production
- **DEBUG**: Set to `False` in production
- **ALLOWED_HOSTS**: Add your domain/IP in production
- **DATABASES**: Configure your production database
- **MEDIA_ROOT**: Location for uploaded files
- **STATIC_ROOT**: Location for static files

### API Keys

The application uses Google API for certain features. Update the API key in `settings.py`:

```python
API_KEY = "your-google-api-key"
```

### Email Configuration (Optional)

For email notifications, add the following to `settings.py`:

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
```

## 📖 Usage

### For Students

1. **Register**: Create an account by selecting "Student" role
2. **Wait for Approval**: Admin must approve your account
3. **Complete Profile**: Fill in all required details
4. **Upload Resume**: Upload your resume for approval
5. **Browse Jobs**: View available job postings
6. **Apply**: Submit applications for eligible positions
7. **Track Progress**: Monitor your applications and notifications

### For Teachers/Placement Officers

1. **Register**: Create an account with "Teacher" role
2. **Get Approved**: Wait for admin approval
3. **Manage Students**: View and approve student profiles/resumes
4. **Create Training**: Schedule and upload training content
5. **Monitor Placements**: Track student placement progress
6. **Generate Reports**: Access placement analytics

### For Companies

1. **Register**: Create a company account
2. **Complete Profile**: Add company details and logo
3. **Post Jobs**: Create job listings with requirements
4. **Review Applications**: View and filter student applications
5. **Access Resumes**: Download student resumes

### For Administrators

1. **Login**: Use superuser credentials
2. **Approve Users**: Review and approve registrations
3. **Manage Programs**: Add/edit degree and specialization options
4. **View Reports**: Access comprehensive placement reports
5. **Send Notifications**: Broadcast important announcements

## 👥 User Roles

| Role | Permissions |
|------|-------------|
| **Student** | View jobs, apply for positions, upload resume, access training |
| **Teacher** | Manage students, create training, approve resumes, view reports |
| **Company** | Post jobs, view applications, access student profiles |
| **Principal/Admin** | Full system access, user approval, reports, system configuration |

## 📁 Project Structure

```
placement/
├── placement/              # Main project directory
│   ├── app/               # Core application
│   │   ├── models.py      # User permissions, notifications, principal
│   │   ├── views.py       # Authentication, dashboard, reports
│   │   └── urls.py        # URL routing
│   ├── student/           # Student module
│   │   ├── models.py      # Student details, job info
│   │   ├── views.py       # Student views
│   │   ├── cgpa.py        # CGPA calculation utilities
│   │   └── urls.py        # Student URLs
│   ├── teacher/           # Teacher module
│   │   ├── models.py      # Teacher details, training
│   │   ├── views.py       # Teacher views
│   │   └── urls.py        # Teacher URLs
│   ├── company/           # Company module
│   │   ├── models.py      # Company details, jobs, applications
│   │   ├── views.py       # Company views
│   │   └── urls.py        # Company URLs
│   ├── templates/         # HTML templates
│   │   ├── app/           # Core templates
│   │   ├── student/       # Student templates
│   │   ├── teacher/       # Teacher templates
│   │   ├── company/       # Company templates
│   │   └── unauthpages/   # Public pages
│   ├── static/            # Static files (CSS, JS, images)
│   ├── media/             # Uploaded files
│   ├── placement/         # Project settings
│   │   ├── settings.py    # Configuration
│   │   ├── urls.py        # Main URL configuration
│   │   └── wsgi.py        # WSGI configuration
│   ├── manage.py          # Django management script
│   └── db.sqlite3         # Database file
```

## 🗄️ Database Models

### Core Models (app)

#### UserPermission
- Manages user roles and permissions
- Fields: `user`, `is_teacher`, `is_company`, `is_student`, `is_principal`, `is_approved`

#### Principal
- Administrator profile
- Fields: `user`, `name`, `email`, `phone`, `address`, `profile_picture`

#### DegreeSpecialization
- Academic programs configuration
- Fields: `user`, `degree`, `specialization`

#### Notification
- System notifications
- Fields: `user`, `teacher`, `admin`, `message`, `is_read`, `date`

### Student Models

#### StudentDetails
- Complete student profile
- Fields: `user`, `name`, `email`, `phone`, `address`, `date_of_birth`, `gender`, `blood_group`, `profile_picture`, `course`, `branch`, `is_passed_out`, `year`, `sem`, `roll_no`, `reg_no`, `cgpa`, `resume`, `is_resume_approved`

#### JobInfo
- Student placement information
- Fields: `student`, `job_title`, `company_name`, `company_location`, `salary`, `date`

### Teacher Models

#### TeacherDetails
- Teacher/faculty profile
- Fields: `user`, `name`, `email`, `phone`, `address`, `date_of_birth`, `gender`, `blood_group`, `profile_picture`, `designation`, `specialization`, `department`, `is_hod`, `is_placement_faculty`

#### Training
- Training sessions
- Fields: `user`, `title`, `description`, `gogle_meet_link`, `date`, `vedio`, `quiz_link`

### Company Models

#### CompanyDetails
- Company profile
- Fields: `user`, `name`, `email`, `phone`, `location`, `industry_type`, `profile_picture`

#### JobDetails
- Job postings
- Fields: `company`, `title`, `description`, `salary`, `location`, `industry_type`, `cgpa_threshold`, `job_type`, `job_mode`, `date_posted`, `is_active`

#### JobApplication
- Student job applications
- Fields: `job`, `user`, `cover_letter`, `available_to_work_in`, `cgpa_required`, `date_applied`, `confirm_info`

## 🔄 Key Workflows

### Student Registration & Placement Flow

```
1. Student Registration
   ↓
2. Admin Approval
   ↓
3. Profile Completion
   ↓
4. Resume Upload
   ↓
5. Teacher Resume Approval
   ↓
6. Browse & Apply for Jobs
   ↓
7. Company Reviews Application
   ↓
8. Placement Confirmation
```

### Training Session Flow

```
1. Teacher Creates Training
   ↓
2. Adds Video/Meet Link/Quiz
   ↓
3. Students Access Training
   ↓
4. Complete Assessments
   ↓
5. Track Progress
```

### Job Posting Flow

```
1. Company Posts Job
   ↓
2. System Filters Eligible Students
   ↓
3. Students Apply
   ↓
4. Company Reviews Applications
   ↓
5. Selection Process
```

## 🚀 Advanced Features

### CGPA Calculation
- Automated CGPA calculation utility (`student/cgpa.py`)
- Supports multiple grading systems
- Semester-wise tracking

### Resume Approval System
- Two-tier approval process
- Teacher/placement officer review
- Status tracking (pending, approved, rejected)

### Eligibility Filtering
- Automatic filtering based on CGPA thresholds
- Course/branch-based filtering
- Year/semester restrictions

### Analytics & Reporting
- Year-wise placement statistics
- Branch-wise analysis
- Company-wise data
- Salary trends
- Placement percentage calculations

## 🔒 Security Features

- Password validation and hashing
- CSRF protection
- SQL injection prevention (Django ORM)
- XSS protection
- Session security
- File upload validation
- Role-based access control

## 🐛 Troubleshooting

### Common Issues

**Issue**: Database errors after migration
```bash
# Solution: Reset migrations
python manage.py migrate --run-syncdb
```

**Issue**: Static files not loading
```bash
# Solution: Collect static files
python manage.py collectstatic --clear
```

**Issue**: Media files not accessible
```bash
# Solution: Check MEDIA_ROOT and MEDIA_URL in settings.py
# Ensure DEBUG=True for development
```

**Issue**: Permission denied errors
```bash
# Solution: Check file permissions
chmod -R 755 media/
chmod -R 755 static/
```

## 📝 Development Guidelines

### Adding New Features

1. Create models in appropriate app's `models.py`
2. Run migrations: `python manage.py makemigrations && python manage.py migrate`
3. Create views in `views.py`
4. Add URL patterns in `urls.py`
5. Create templates in `templates/` directory
6. Test thoroughly before deployment

### Code Style

- Follow PEP 8 guidelines
- Use meaningful variable names
- Add comments for complex logic
- Keep functions focused and small

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👨‍💻 Author

Developed as a comprehensive placement management solution for educational institutions.

## 📞 Support

For issues, questions, or contributions, please open an issue in the repository.

## 🙏 Acknowledgments

- Django Documentation
- Bootstrap Framework
- Google APIs
- Open Source Community

---

**Note**: This is a development version. For production deployment, ensure proper security configurations, use a production-grade database (PostgreSQL/MySQL), set DEBUG=False, configure proper ALLOWED_HOSTS, and use environment variables for sensitive data.
