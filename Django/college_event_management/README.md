# College Event Management System

A comprehensive Django-based web application designed to manage college events, student registrations, MCQ examinations, certificate generation, and academic records (SGPA/CGPA tracking).

## 📋 Table of Contents

- [Features](#features)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [User Roles](#user-roles)
- [Key Functionalities](#key-functionalities)
- [Database Models](#database-models)
- [Screenshots](#screenshots)
- [Contributing](#contributing)
- [License](#license)

## ✨ Features

### 🎯 Core Features

- **Event Management**: Create, update, and delete college events with detailed information
- **Student Registration**: Students can register for events with project details
- **MCQ Examination System**: Create and conduct online MCQ tests linked to events
- **Certificate Generation**: Automatic PDF certificate generation with QR code verification
- **Gallery Management**: Upload and manage event photos with captions
- **Student Approval System**: Admin approval workflow for new student registrations
- **Academic Records**: Complete SGPA/CGPA tracking system with semester-wise subject management
- **Notification System**: Event-based notifications for students
- **Profile Management**: Comprehensive user profiles with academic and personal information
- **Export Functionality**: Export event participant data to Excel

### 🔐 Authentication & Authorization

- User registration and login system
- Role-based access control (Coordinator/Student)
- Password change functionality
- Session management

## 🛠 Technology Stack

- **Backend**: Django 5.2.5
- **Database**: SQLite3
- **Frontend**: HTML, CSS, JavaScript
- **Image Processing**: Pillow (PIL)
- **QR Code Generation**: qrcode library
- **Excel Export**: openpyxl
- **Template Engine**: Django Templates

## 📁 Project Structure

```
college_event_management/
├── Coordinator/                 # Coordinator app (admin/staff functionality)
│   ├── models.py               # Database models
│   ├── views.py                # View functions
│   ├── urls.py                 # URL routing
│   ├── admin.py                # Admin panel configuration
│   └── templates/              # Coordinator templates
│       ├── dashboard.html
│       ├── MCQ.html
│       ├── create_mcq.html
│       ├── edit_form.html
│       ├── form.html
│       ├── notification.html
│       ├── profile.html
│       └── approve_student.html
├── student/                    # Student app
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── certificate.py          # Certificate generation logic
│   ├── course_data.py          # Semester course data
│   └── templates/              # Student templates
│       ├── dashboard.html
│       ├── mcq_exam.html
│       ├── my_certificates.html
│       └── profile.html
├── templates/                  # Shared templates
│   ├── base.html
│   └── unauth/                 # Unauthenticated user templates
│       ├── index.html
│       ├── login.html
│       ├── register.html
│       ├── event.html
│       ├── gallery.html
│       ├── change_password.html
│       └── verify_certificate.html
├── static/                     # Static files (CSS, JS, Images, Fonts)
├── media/                      # User-uploaded files
│   ├── profile/
│   ├── events/
│   ├── galary/
│   └── certificates/
├── college_event_management/   # Project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── db.sqlite3                  # SQLite database
└── manage.py                   # Django management script
```

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Setup Instructions

1. **Clone the repository**
   ```bash
   cd /Volumes/CrucialX9/Project/Django/college_event_management
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On macOS/Linux
   # or
   venv\Scripts\activate  # On Windows
   ```

3. **Install required packages**
   ```bash
   pip install django pillow qrcode openpyxl
   ```

4. **Apply database migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create a superuser** (for admin access)
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server**
   ```bash
   python manage.py runserver
   ```

7. **Access the application**
   - Main site: `http://localhost:8000/`
   - Admin panel: `http://localhost:8000/admin/`
   - Student portal: `http://localhost:8000/students/`

## 📖 Usage

### For Coordinators/Admins

1. **Login** at `/login/` with coordinator credentials
2. **Dashboard**: View statistics, upcoming events, and recent registrations
3. **Create Events**: Add new events with details, images, and optional MCQ tests
4. **Manage MCQs**: Create, edit, and toggle MCQ test status
5. **Approve Students**: Review and approve new student registrations
6. **Gallery Management**: Upload event photos with captions
7. **Send Notifications**: Notify students about events
8. **Export Data**: Download participant lists as Excel files
9. **Verify Certificates**: Scan QR codes to verify certificate authenticity

### For Students

1. **Register** at `/register/` and wait for admin approval
2. **Login** at `/login/` after approval
3. **Browse Events**: View all upcoming and past events
4. **Register for Events**: Sign up for events with project details
5. **Take MCQ Tests**: Participate in event-related examinations
6. **View Certificates**: Access earned certificates with QR verification
7. **Manage Profile**: Update personal and academic information
8. **Track SGPA/CGPA**: Add semester grades and view calculated CGPA

## 👥 User Roles

### Coordinator/Admin
- Full access to event management
- Student approval authority
- MCQ creation and management
- Certificate generation
- Gallery management
- Notification broadcasting
- Data export capabilities

### Student
- Event browsing and registration
- MCQ examination participation
- Certificate viewing and download
- Profile management
- Academic record tracking (SGPA/CGPA)
- Event cancellation

## 🎓 Key Functionalities

### 1. Event Management
- Create events with name, date, location, description, and image
- Link MCQ tests to events
- Track event registrations
- Export participant data to Excel
- Delete events with cascade deletion of related data

### 2. MCQ Examination System
- Create MCQ tests with title, duration, and number of questions
- Add multiple-choice questions with 4 options
- Auto-grading system
- Time-limited examinations
- Toggle test active/inactive status
- Edit existing MCQs and questions

### 3. Certificate Generation
- **Participation Certificates**: Generated for event attendees
- **Achievement Certificates**: Generated for MCQ test passers
- QR code integration for verification
- Custom certificate templates with Poppins font
- PDF format for easy download and printing
- Unique certificate IDs

### 4. Academic Record System
- **Profile Management**: Store student details (admission no, branch, year, CGPA, etc.)
- **Semester SGPA Tracking**: Add subjects with grades and credits
- **Automatic CGPA Calculation**: Weighted average based on credits
- **Grade Point Mapping**: S(10), A(9), B(8), C(7), D(6), E(5), F(0)
- **Course Data**: Pre-defined semester-wise course structure

### 5. Gallery System
- Upload event photos
- Add captions and categorize by type
- Date-stamped entries
- Delete functionality

### 6. Notification System
- Event-based notifications
- Targeted messaging to students
- Timestamp tracking

### 7. Student Approval Workflow
- New registrations require admin approval
- Pending approval page for students
- Bulk approve/unapprove functionality
- Status tracking in student list

## 🗄 Database Models

### Profile
Stores user profile information including:
- User relationship (OneToOne with Django User)
- Type (Student/Coordinator)
- Contact details (phone, address)
- Academic info (admission no, registration no, branch, year)
- Personal details (DOB, father/mother name)
- Academic performance (CGPA, 10th, 12th marks)
- Profile picture

### StudentSGPA
Tracks semester-wise SGPA:
- Student reference
- Semester identifier
- SGPA value (auto-calculated)
- Total credits
- Timestamps

### Subject
Individual subject records:
- Subject name and code
- Credits
- Grade (letter grade)
- Grade point (auto-converted from letter grade)
- Linked to StudentSGPA

### Events
Event information:
- Event name, date, location
- Event type
- Description and image
- Optional MCQ test link
- Creator reference

### EventRegister
Student event registrations:
- User and event references
- Project title and description
- Team members
- Branch
- Registration timestamp

### Mcq
MCQ test details:
- Title and duration
- Number of questions
- Active status
- Date
- Creator reference

### Question
MCQ questions:
- Question text
- Four options
- Correct answer
- Linked to MCQ

### Certificate
Certificate records:
- User and event references
- Unique certificate ID
- Pass/fail status
- PDF file path
- Generation timestamp

### Gallery
Photo gallery:
- Image file
- Caption
- Gallery type
- Upload date
- Uploader reference

### Notification
Event notifications:
- User and event references
- Message content
- Timestamp

## 🎨 Design Features

- **Responsive Design**: Mobile-friendly interface
- **Modern UI**: Clean and professional design
- **Custom Fonts**: Poppins font family for certificates
- **QR Code Integration**: Certificate verification system
- **Image Upload**: Support for profile pictures and event images
- **Dynamic Forms**: AJAX-based form submissions
- **Data Validation**: Client and server-side validation

## 📊 Statistics & Analytics

The coordinator dashboard displays:
- Total number of events
- Total student registrations
- Upcoming events count
- Recent registrations
- Event-wise participant counts

## 🔒 Security Features

- CSRF protection
- Password validation
- Session management
- User authentication required for protected routes
- Role-based access control
- Secure file uploads

## 🌐 URL Structure

### Coordinator Routes (`/`)
- `/` - Home page
- `/login/` - Login page
- `/register/` - Registration page
- `/logout/` - Logout
- `/dashboard/` - Coordinator dashboard
- `/event/` - Event management
- `/gallery/` - Gallery management
- `/mcq/` - MCQ management
- `/profile/` - Profile page
- `/approve_students/` - Student approval
- `/notification/` - Send notifications
- `/verify_certificate/<cert_id>/` - Certificate verification
- `/change_password/` - Password change

### Student Routes (`/students/`)
- `/students/` - Student dashboard
- `/students/register_event` - Event registration
- `/students/cancel_register` - Cancel registration
- `/students/mcq_exam/<id>/` - Take MCQ exam
- `/students/profile` - Student profile
- `/students/my_certificates` - View certificates
- `/students/handle_sgpa` - Manage SGPA records

## 📝 Future Enhancements

Potential improvements for the system:
- Email notifications
- Payment gateway integration for paid events
- Advanced analytics and reporting
- Mobile app development
- Real-time chat support
- Event calendar integration
- Attendance tracking with QR codes
- Multi-language support
- Advanced search and filtering
- API development for third-party integrations

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is developed for educational purposes as part of a college project.

## 👨‍💻 Developer

Developed by Jonah Jayasingh

## 📞 Support

For support, please contact the development team or raise an issue in the repository.

---

**Note**: This is a development version. For production deployment, ensure to:
- Change `DEBUG = False` in settings.py
- Set a strong `SECRET_KEY`
- Configure proper database (PostgreSQL/MySQL)
- Set up static file serving
- Configure ALLOWED_HOSTS
- Enable HTTPS
- Set up proper logging
- Implement backup strategies
