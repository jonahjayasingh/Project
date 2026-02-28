# Food Donation Management System

A comprehensive Django-based platform designed to bridge the gap between food donors and those in need. The system features an AI-powered chatbot for seamless donation entry, smart geolocation for optimized logistics, and a secure verification system.

## 🌟 Key Features

### 1. AI-Powered Donation Assistant

- **Conversational Interface**: Create donations simply by chatting with an AI assistant.
- **Smart Extraction**: Automatically extracts food type, quantity, and pickup details from natural language.
- **State-Aware Logic**: Remembers context and handles updates to donation details during conversation.
- **Ollama Integration**: Powered by local LLMs (e.g., cogito-2.1) via Ollama.

### 2. Smart Logistics & Map Integration

- **Live Location Selection**: Interactive map (Leaflet.js) for precise pickup spot marking.
- **Distance Calculation**: NGOs and volunteers see real-time distance from their location to the food source.
- **Area-Specific Rejection**: When an NGO rejects a donation, it remains available for other NGOs in the vicinity.

### 3. Role-Based Ecosystem

- **Donor**: Post food donations, track fulfillment, and manage their profile.
- **NGO**: Browse available donations within a 20km radius, accept/reject pickups, and assign volunteers.
- **Volunteer**: Manage assigned tasks with a 15km pickup limit and real-time navigation support.
- **Admin**: Oversee the entire system, approve users, and manage all donation records.

### 4. Secure Fulfillment

- **OTP Verification**: Two-step secure verification:
  - **Pickup OTP**: Donor provides a 6-digit code to the volunteer to confirm pickup.
  - **Delivery OTP**: NGO provides a 6-digit code to the volunteer to confirm final delivery.
- **Status History**: Full audit trail of every status change (Pending → Accepted → Picked → Delivered).

## 🛠️ Technical Stack

- **Backend**: Django 5.x (Python)
- **Frontend**: Bootstrap 5, Vanilla JavaScript
- **Mapping**: Leaflet.js, OpenStreetMap API
- **AI Engine**: Ollama (Cogito model)
- **Database**: SQLite (Development)

## 🚀 Newly Implemented Production Features (v2.0)

### 🥑 Food Safety & Expiry System

- **Automated Expiry Calculation**: Donations expire 6 hours after cooking by default.
- **Background Cleanup**: Celery tasks automatically mark expired donations and notify donors.
- **Real-Time Countdown**: Detail pages show a live timer for food safety.
- **Smart Filtering**: NGOs cannot see or accept expired food.

### 📧 Automated Notifications

- **Email Alerts**: Triggered on creation, acceptance, pickup, and delivery.
- **OTP Delivery**: Verification codes sent to donors and NGOs via email.
- **Expiry Warnings**: Background jobs send alerts when food is nearing expiry.

### 📊 Advanced Management Control

- **Custom Admin Panel**: Integrated dashboard for system-wide oversight (NO Django Admin).
- **Audit Logging**: Every critical action (acceptance, user approval, deletion) is logged.
- **Data Maintenance**: Manual and automated archiving for records older than 30 days.
- **User Verification**: Admin-controlled approval workflow for NGOs and Volunteers.

### 🗺️ Live Operations & Tracking

- **Status Polling**: Dashboards auto-refresh using JSON polling (no WebSockets required).
- **Navigation Integration**: One-click Google Maps directions for volunteers.
- **Priority Alerts**: "URGENT" badges for donations nearing safe consumption limits.
- **NGO-Specific Rejection**: Rejections are now NGO-specific, keeping donations available for the community.

## 🚀 Setup Instructions

### Prerequisites

- Python 3.10+
- Ollama (Running locally on port 11434)

### Installation

1. **Clone the repository**:

   ```bash
   git clone <repository-url>
   cd "Food Donation Management System"
   ```

2. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Run Migrations**:

   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

4. **Start the AI Server**:
   Ensure Ollama is running and has the required model:

   ```bash
   ollama run cogito-2.1:671b-cloud
   ```

5. **Start the Django Server**:
   ```bash
   python manage.py runserver
   ```

## 🔐 System Access

By default, all user passwords for the testing environment have been updated to `1` for convenience across all roles (Donor, NGO, Volunteer).

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
