# Gym Management System

A comprehensive Django-based gym management system with role-based authentication, member management, class scheduling, attendance tracking, and payment processing.

## Features

### Core Functionality
- ✅ **Role-Based Authentication** - Admin, Staff, Trainer, and Member roles
- ✅ **Member Management** - Complete member profiles with health information
- ✅ **Membership Plans** - Flexible subscription plans with auto-expiry
- ✅ **Trainer Management** - Trainer profiles, schedules, and member assignments
- ✅ **Class Scheduling** - Fitness classes with capacity management and waitlists
- ✅ **Attendance Tracking** - Check-in/check-out with duration calculation
- ✅ **Payment Processing** - Multiple payment methods and invoice generation
- ✅ **Analytics Dashboards** - Role-specific dashboards with statistics

### User Roles

#### Admin/Staff
- View comprehensive analytics and statistics
- Manage all members, trainers, and classes
- Track revenue and payments
- Monitor attendance trends
- Access Django admin panel

#### Trainer
- View assigned members
- Manage class schedules
- Track today's classes
- View weekly schedule

#### Member
- View membership status and expiry
- Track attendance history
- View upcoming class bookings
- Check payment history

## Technology Stack

- **Backend:** Django 5.2.5
- **Database:** SQLite (development) / PostgreSQL (production-ready)
- **Frontend:** Bootstrap 5, HTML5, CSS3
- **Icons:** Bootstrap Icons
- **Fonts:** Google Fonts (Inter)
- **Python:** 3.10+

## Installation

### Prerequisites
- Python 3.10 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### Setup Steps

1. **Clone or navigate to the project directory**
   ```bash
   cd /Volumes/CrucialX9/Project/Django/Gym_management_system
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations**
   ```bash
   python manage.py migrate
   ```

5. **Create superuser**
   ```bash
   python manage.py create_admin
   ```
   
   Or create a custom superuser:
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server**
   ```bash
   python manage.py runserver
   ```

7. **Access the application**
   - Main site: http://localhost:8000
   - Admin panel: http://localhost:8000/admin/

## Default Credentials

**Superuser Account:**
- Username: `admin`
- Password: `admin123`
- Email: `admin@gymmanagementsystem.com`

> ⚠️ **Important:** Change these credentials in production!

## Project Structure

```
Gym_management_system/
├── accounts/              # User authentication & management
│   ├── models.py         # CustomUser model
│   ├── views.py          # Login, logout, profile views
│   └── admin.py          # Admin configuration
├── members/              # Member profiles
│   ├── models.py         # Member model
│   └── admin.py          # Member admin
├── trainers/             # Trainer management
│   ├── models.py         # Trainer, Availability, Assignment models
│   └── admin.py          # Trainer admin
├── memberships/          # Plans & subscriptions
│   ├── models.py         # MembershipPlan, MemberMembership models
│   └── admin.py          # Membership admin
├── attendance/           # Check-in tracking
│   ├── models.py         # Attendance model
│   └── admin.py          # Attendance admin
├── classes/              # Class scheduling
│   ├── models.py         # FitnessClass, Schedule, Booking models
│   └── admin.py          # Class admin
├── payments/             # Payment processing
│   ├── models.py         # Payment, Invoice models
│   └── admin.py          # Payment admin
├── dashboard/            # Analytics dashboards
│   ├── views.py          # Dashboard views for all roles
│   └── urls.py           # Dashboard URLs
├── templates/            # HTML templates
│   ├── base.html         # Base template
│   ├── accounts/         # Authentication templates
│   └── dashboard/        # Dashboard templates
├── static/               # Static files (CSS, JS, images)
├── media/                # User uploads
└── manage.py             # Django management script
```

## Database Models

### CustomUser
- Extended Django User with role, phone, DOB, gender, address, profile photo
- Roles: Admin, Staff, Trainer, Member

### Member
- Emergency contact, blood group, medical notes
- Height, weight, fitness goals
- Status: Active, Inactive, Frozen

### MembershipPlan
- Duration (1, 3, 6, 12 months)
- Access levels: Gym Only, Gym + Classes, Premium
- Price and benefits

### MemberMembership
- Links members to plans
- Auto-calculated expiry dates
- Freeze/unfreeze functionality
- Payment tracking

### Trainer
- Specialization, certifications, experience
- Hourly rate, availability status

### FitnessClass
- Class types with difficulty levels
- Capacity management
- Weekly schedules

### Attendance
- Check-in/check-out timestamps
- Duration calculation
- Type tracking

### Payment
- Auto-generated invoice numbers
- Multiple payment methods
- Status tracking

## Usage

### Admin Panel
1. Login with admin credentials
2. Navigate to http://localhost:8000/admin/
3. Manage all aspects of the system:
   - Add/edit members
   - Create membership plans
   - Assign trainers
   - Schedule classes
   - Record payments
   - Track attendance

### Dashboards
- **Admin Dashboard:** `/dashboard/admin/` - Analytics and statistics
- **Member Dashboard:** `/dashboard/member/` - Personal membership info
- **Trainer Dashboard:** `/dashboard/trainer/` - Schedule and assignments

## Development

### Adding New Features
The system is designed to be extensible. Common additions:

1. **CRUD Interfaces** - Add web forms for creating/editing records
2. **Search & Filters** - Implement advanced filtering
3. **Reports** - Generate PDF reports
4. **Charts** - Add Chart.js visualizations
5. **Notifications** - Email/SMS alerts
6. **QR Codes** - QR-based check-in system
7. **Payment Gateway** - Integrate Stripe/Razorpay

### Running Tests
```bash
python manage.py test
```

### Collecting Static Files (for production)
```bash
python manage.py collectstatic
```

## Configuration

### Email Settings
Update `settings.py` for production email:
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-password'
```

### Database (Production)
For PostgreSQL:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'gym_db',
        'USER': 'gym_user',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## Security Notes

- Change `SECRET_KEY` in production
- Set `DEBUG = False` in production
- Configure `ALLOWED_HOSTS`
- Use environment variables for sensitive data
- Enable HTTPS in production
- Regular database backups

## Contributing

This is a project template. Feel free to:
- Add new features
- Improve UI/UX
- Add tests
- Optimize queries
- Add documentation

## License

This project is open source and available for educational and commercial use.

## Support

For issues or questions:
- Check the Django documentation: https://docs.djangoproject.com/
- Review the code comments
- Consult the walkthrough.md file

## Changelog

### Version 1.0.0 (2026-01-02)
- Initial release
- Core authentication system
- Database models for all entities
- Admin panel integration
- Role-based dashboards
- Responsive UI with Bootstrap 5
- Basic analytics and statistics

---

**Built with ❤️ using Django**
