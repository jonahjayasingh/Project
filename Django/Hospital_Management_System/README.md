# Hospital Management System

A comprehensive Django-based Hospital Management System with role-based access control, patient management, appointment scheduling, billing, pharmacy management, and more.

## Features

### 1. **Authentication & Authorization**
- Custom User model with role-based access (Admin, Doctor, Nurse, Receptionist, Patient)
- Login/Logout functionality
- User registration
- Profile management
- Role-based permissions

### 2. **Patient Management**
- Patient registration with complete profile
- Medical history tracking
- Emergency contact information
- Blood group, height, weight tracking
- Patient status management (Active, Discharged, Deceased)
- Document upload (reports, scans, prescriptions)
- Search and filtering capabilities

### 3. **Doctor Management**
- Doctor profiles with specialization
- Qualifications and experience tracking
- Department assignment
- Availability schedule management
- Consultation fee management
- License number tracking

### 4. **Department Management**
- Multiple departments (Cardiology, Neurology, Orthopedics, etc.)
- Department head assignment
- Staff allocation by department

### 5. **Appointment System**
- Appointment booking
- Appointment scheduling with time slots
- Overlap prevention (no double-booking)
- Appointment status tracking (Scheduled, Confirmed, Completed, Cancelled)
- Appointment rescheduling and cancellation
- Doctor-wise and patient-wise appointment views

### 6. **Nurse Module**
- Nurse profiles with qualifications
- Department assignment
- Shift tracking (Morning, Afternoon, Night)
- Patient assignment system
- Nurse dashboard with assigned patients

### 7. **Medical Records & Treatment**
- Comprehensive medical records
- Diagnosis and symptoms tracking
- Treatment plans
- Vital signs recording (Temperature, BP, Pulse, etc.)
- Lab reports and test results
- Medical history timeline
- Prescription management

### 8. **Pharmacy Management**
- Medicine inventory with stock tracking
- Low-stock alerts
- Prescription creation and management
- Medicine dispensing workflow
- Dosage and frequency tracking
- Batch number and expiry date management

### 9. **Billing & Payments**
- Comprehensive billing system
- Multiple charge types (Consultation, Medicine, Room, Lab)
- Automatic total calculation
- Payment tracking
- Multiple payment methods (Cash, Card, UPI, Online, Insurance)
- Payment status management
- Billing history

### 10. **Room & Bed Management**
- Room types (General, Private, ICU, Emergency, Operation Theater)
- Bed availability tracking
- Patient admission workflow
- Discharge management
- Automatic bed occupancy updates
- Room charges calculation

### 11. **Role-Based Dashboards**
- **Admin Dashboard**: Overall statistics, revenue, bed availability, alerts
- **Doctor Dashboard**: Today's appointments, patient list, upcoming appointments
- **Nurse Dashboard**: Assigned patients, department info
- **Receptionist Dashboard**: Appointments, admissions, available beds
- **Patient Dashboard**: Upcoming appointments, medical records, bills, prescriptions

### 12. **Security Features**
- CSRF protection
- Secure file uploads
- Permission checks on views
- Session security
- XSS protection
- Secure password hashing

## Technology Stack

- **Backend**: Django 5.2.9
- **Database**: SQLite (Development), PostgreSQL-ready (Production)
- **Frontend**: Bootstrap 5, Bootstrap Icons
- **Forms**: Django Crispy Forms with Bootstrap 4
- **File Handling**: Pillow for image processing
- **PDF Generation**: ReportLab
- **Environment Management**: Python Decouple

## Installation

### Prerequisites
- Python 3.10 or higher
- pip
- Virtual environment (recommended)

### Setup Instructions

1. **Clone the repository** (if applicable)
   ```bash
   cd /Volumes/CrucialX9/Project/Django/Hospital_Management_System
   ```

2. **Virtual environment is already created**
   ```bash
   source venv/bin/activate
   ```

3. **Install dependencies** (already installed)
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment variables** (already configured in `.env`)
   - SECRET_KEY
   - DEBUG
   - Database settings
   - Email settings

5. **Run migrations** (already done)
   ```bash
   python manage.py migrate
   ```

6. **Create initial data** (already done)
   ```bash
   python manage.py setup_initial_data
   ```

7. **Run the development server**
   ```bash
   python manage.py runserver
   ```

8. **Access the application**
   - Main application: http://127.0.0.1:8000/
   - Admin panel: http://127.0.0.1:8000/admin/

## Default Login Credentials

### Admin
- **Username**: admin
- **Password**: admin123

### Doctor
- **Username**: doctor1
- **Password**: doctor123

### Nurse
- **Username**: nurse1
- **Password**: nurse123

### Receptionist
- **Username**: receptionist1
- **Password**: reception123

### Patient
- **Username**: patient1
- **Password**: patient123

## Project Structure

```
Hospital_Management_System/
├── accounts/              # User authentication and profiles
├── patients/              # Patient management
├── doctors/               # Doctor and department management
├── nurses/                # Nurse management
├── appointments/          # Appointment scheduling
├── medical_records/       # Medical records and lab reports
├── pharmacy/              # Medicine and prescription management
├── billing/               # Billing and payment management
├── rooms/                 # Room and bed management
├── dashboard/             # Role-based dashboards
├── hospital_system/       # Main project settings
├── templates/             # HTML templates
├── static/                # Static files (CSS, JS, images)
├── media/                 # User-uploaded files
├── manage.py              # Django management script
├── requirements.txt       # Python dependencies
└── .env                   # Environment variables
```

## Database Models

### Core Models
- **User**: Custom user model with role-based access
- **Patient**: Patient profiles and medical history
- **Doctor**: Doctor profiles with specialization
- **Nurse**: Nurse profiles with shift management
- **Department**: Hospital departments

### Operational Models
- **Appointment**: Appointment scheduling
- **MedicalRecord**: Patient medical records
- **LabReport**: Laboratory test results
- **Prescription**: Medicine prescriptions
- **PrescriptionItem**: Individual prescription items
- **Medicine**: Medicine inventory

### Financial Models
- **Bill**: Patient billing
- **Payment**: Payment transactions

### Facility Models
- **Room**: Hospital rooms
- **Bed**: Hospital beds
- **Admission**: Patient admissions

## Admin Panel Features

The Django admin panel provides comprehensive management capabilities:

- User management with role assignment
- Patient CRUD with inline documents
- Doctor and department management
- Appointment scheduling with validation
- Medical records with inline lab reports
- Prescription management with inline items
- Billing with inline payments
- Room and bed management with inline beds
- Custom filters and search functionality
- Read-only fields for auto-generated IDs

## API Endpoints (Future Enhancement)

The system is designed to support REST API integration for:
- Mobile applications
- Third-party integrations
- Reporting systems
- Analytics dashboards

## Production Deployment

### PostgreSQL Configuration

Update `.env` file:
```env
DB_ENGINE=django.db.backends.postgresql
DB_NAME=hospital_db
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

### Static Files

```bash
python manage.py collectstatic
```

### Security Checklist

- [ ] Set DEBUG=False
- [ ] Update SECRET_KEY
- [ ] Configure ALLOWED_HOSTS
- [ ] Set up HTTPS
- [ ] Configure email backend
- [ ] Set up database backups
- [ ] Configure logging
- [ ] Set up monitoring

## Future Enhancements

1. **Notifications**
   - Email notifications for appointments
   - SMS reminders
   - Push notifications

2. **Reporting**
   - PDF invoice generation
   - Medical report generation
   - Analytics dashboards
   - Revenue reports

3. **Advanced Features**
   - Video consultation
   - Online appointment booking
   - Patient portal
   - Doctor availability calendar
   - Inventory management
   - Insurance claim processing

4. **Mobile Application**
   - Patient mobile app
   - Doctor mobile app
   - Staff mobile app

## Contributing

This is a comprehensive hospital management system designed for educational and production use. Contributions are welcome!

## License

This project is open-source and available for educational and commercial use.

## Support

For issues, questions, or contributions, please refer to the project documentation or contact the development team.

## Acknowledgments

- Django Framework
- Bootstrap
- Bootstrap Icons
- All open-source contributors

---

**Version**: 1.0.0  
**Last Updated**: January 6, 2026  
**Developer**: Hospital Management System Team
