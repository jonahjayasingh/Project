# 🎓 College Event Management System

A comprehensive, dual-portal Django ecosystem designed for modern academic institutions to manage events, automated assessments, and student academic performance.

---

## 🚀 Quick Setup

### 1. Environment & Dependencies

```bash
# Clone the repository
git clone <repository-url>
cd college_event_management

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # MacOS/Linux
# venv\Scripts\activate   # Windows

# Install requirements
pip install -r requirements.txt
```

### 2. Database Initialization

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### 3. Launch

```bash
python manage.py runserver
```

---

## 🏗️ System Architecture

### 1. **Coordinator Dashbaord** (Admin/Staff)

The central hub for institutional management, featuring:

- **Event Lifecycle**: CRUD operations for workshops, exhibitions, and seminars.
- **Dynamic MCQ Engine**: Interactive form builder to create time-bound assessments.
- **Student Approval System**: Workflow to verify and authorize new student accounts.
- **Gallery Management**: Organization of event memorabilia with categorized uploads.
- **Broadcast System**: Instant notifications linked to specific academic events.
- **Data Intelligence**: Export participant lists directly to formatted Excel (.xlsx) files.

### 2. **Student Portal**

A personalized experience for academic and extracurricular growth:

- **Interactive Dashboard**: Real-time tracking of upcoming events and active registrations.
- **Examination Center**: Participatory interface for MCQ tests with automated grading.
- **Academic Vault**: Manage SGPA/CGPA via a credit-weighted tracking system.
- **Credential Storage**: Access and download QR-coded certificates for participation and achievements.

### 3. **Smart Certificate System**

- **Automated Generation**: Instant PDF creation using PIL (Pillow).
- **QR Verification**: Every certificate includes a unique QR code for instant authenticity verification via protected routes.
- **Dual Classification**: Distinct templates for "Participation" (attendance) and "Achievement" (passing MCQs).

---

## 📊 Technical Schematics

### **Database Model Schema**

| Entity        | Description      | Key Capabilities                                                           |
| :------------ | :--------------- | :------------------------------------------------------------------------- |
| `Profile`     | User Extension   | Academic tracking (CGPA), branch/year mapping, and automated calculations. |
| `Events`      | Event Registry   | Links to MCQs, creators, and handles automated cascade deletions.          |
| `Mcq`         | Assessment Logic | Configurable durations, active status toggles, and question banks.         |
| `StudentSGPA` | Academic Engine  | Real-time weighted average calculation for semester grades.                |
| `Certificate` | Proof of Work    | UUID-based IDs, PDF file generation, and link back to events/users.        |

---

## � Project Visualization

### **Activity Flow**

![Activity Diagram](Image%20for%20report/Activity%20diagram.drawio.png)

### **Use Case Architecture**

![Use Case Diagram](Image%20for%20report/case%20diagram.drawio.png)

### **Sequence Logic**

![Sequence Diagram](Image%20for%20report/sequence.drawio.png)

---

## 🛠️ Technology Stack

- **Backend Framework**: Django 5.2.5
- **Core Libraries**:
  - `Pillow`: Dynamic certificate and image processing.
  - `qrcode`: Secure verification generation.
  - `openpyxl`: Excel report automation.
- **Frontend**: Responsive modern UI using Vanilla CSS and JavaScript.
- **Fonts**: Premium `Poppins` typography for professional document generation.

---

## � Engineering Standards

This project follows the **Antigravity Engineering Doctrine**:

- **Clarity Core**: No hidden side effects; data contracts are strictly enforced.
- **Self-Documenting**: Models use descriptive naming and atomic functions (e.g., `calculate_cgpa`).
- **Deterministic**: Standardized grade-to-point mapping for academic fairness.

---

## 👨‍💻 Maintainers

- **Developer**: Jonah Jayasingh
- **Project Scope**: College Event Management & Academic Records

> [!IMPORTANT]
> **Production Notice**: Move `API_KEY` and `SECRET_KEY` from `settings.py` to a secure environment storage before public deployment.
