# Laboratory Management System (LMS)

A comprehensive Django-based web application designed to streamline diagnostic lab operations, manage patient appointments, process test results, and facilitate secure communication between patients and laboratories.

## 📖 Overview

The **Laboratory Management System** serves as a centralized platform connecting patients with diagnostic labs. It provides:
- **Patients** with a seamless booking experience for lab tests and packages.
- **Laboratories** with tools to manage tests, technicians, bookings, and reports.
- **Administrators** with oversight capabilities for lab approvals and system monitoring.

## ✨ Key Features

### 🏥 Patient Portal
- **Dashboard**: View upcoming appointments, past test history, and reports.
- **Lab Discovery**: Search and filter labs based on available tests and location.
- **Test Booking**: Book individual tests or discounted packages.
- **Appointment Management**: Reschedule or cancel bookings directly.
- **Payments**: Upload payment proofs for verification.
- **Reports**: Securely access and download test reports (with version history).
- **Reviews**: Rate and review lab services.

### 🔬 Lab Portal
- **Dashboard**: Overview of daily appointments, pending approvals, and revenue.
- **Test & Package Management**: Add, edit, and delete tests and packages.
- **Booking Management**: Confirm bookings, update statuses (Pending -> Confirmed -> Sample Collected -> Processing -> Completed).
- **Staff Management**: Add technicians and assign them to specific bookings.
- **Report Upload**: Upload test reports and manage report versions.
- **Financials**: Verify patient payment proofs.
- **Lab Configuration**: Manage operating hours and holidays.

### 🛡️ Admin Portal
- **Lab Approval**: Review and approve new lab registrations.
- **User Management**: Manage patient and lab user accounts.
- **System Settings**: Configure global system parameters.
- **Activity Logs**: Track system-wide activities for security and auditing.
- **Analytics**: Export data for analysis.

### 🔔 System-Wide Features
- **Notifications**: Real-time alerts for booking updates and report availability.
- **Security**: Role-based access control and secure report serving.

## 🛠️ Technology Stack

- **Backend Folder**: Python, Django
- **Frontend**: HTML5, CSS3, JavaScript (Django Templates)
- **Database**: SQLite (default), extensible to PostgreSQL/MySQL
- **Authentication**: Django Auth System

## 🚀 Installation & Setup

1.  **Clone the Repository**
    ```bash
    git clone <repository-url>
    cd "Laboratory Management System"
    ```

2.  **Create a Virtual Environment** (Recommended)
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install Dependencies**
    *(Note: Ensure `django` and `pillow` are installed)*
    ```bash
    pip install django pillow
    ```

4.  **Apply Migrations**
    Initialize the database schema.
    ```bash
    python manage.py migrate
    ```

5.  **Create a Superuser**
    Create an admin account to access the Django admin panel and LMS admin dashboard.
    ```bash
    python manage.py createsuperuser
    ```

6.  **Run the Development Server**
    ```bash
    python manage.py runserver
    ```
    Access the application at `http://127.0.0.1:8000/`.

## 📂 Management Scripts

The project includes several utility scripts to help set up and manage data:

- `seed_labs.py`: Populates the database with sample lab data.
- `seed_patients.py`: Creates sample patient profiles.
- `seed_static.py`: Seeds static data like common test types.
- `approve_labs.py`: Script to quickly approve pending labs.
- `init_tech.py`: Initializes technician roles/data.

**Usage Example:**
```bash
python manage.py shell < seed_labs.py
```

## 📝 Usage Guide

### Logging In
- **Admin**: Go to `/admin/` (Django Admin) or `/dashboard/admin/`.
- **Lab**: Register via `/register/lab/` and login at `/login/lab/`.
- **Patient**: Register via `/register/patient/` and login at `/login/patient/`.

### Common Workflows
1.  **Lab Registration**: A lab registers and awaits admin approval.
2.  **Test Creation**: Approved lab logs in and adds tests/packages.
3.  **Booking**: Patient finds the lab, books a test, and uploads payment proof.
4.  **Process**: Lab verifies payment, assigns a technician (optional), collects sample, and uploads the report.
5.  **Completion**: Patient receives a notification, logs in, and downloads the report.

## 🤝 Contributing

Contributions are welcome! Please fork the repository and submit a pull request.

---
*Generated for the Laboratory Management System Project.*
