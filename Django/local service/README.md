# ServiceFinder - Premium Local Service Marketplace 📍✨

ServiceFinder is a high-end, intelligent marketplace connecting users with elite service professionals. Built with a focus on **Premium Design (Glassmorphism)**, **Location Intelligence**, and **AI-Driven Discovery**, it provides a seamless bridge between clients and local experts.

---

## 🚀 Key Features

### 💎 Cinematic Provider Profiles

- **Premium Visuals**: High-contrast, glassmorphism headers with profile glows and cinematic gradients.
- **Interactive Booking**: Sliding date selection and real-time cost calculators.
- **Vetted Verification**: Professional badges and real-time review systems ensure quality.

### 🗺️ Location Intelligence Dashboard

- **Live Routing**: Both clients and providers can view real-time routes to job locations using **Leaflet Routing Machine**.
- **Visual Workspace**: Map-integrated request management for providers to track their daily service pipeline.
- **Precision Mapping**: Interactive map picker on profile updates with **Auto-Geocoding (OSM)** for neighborhood detection.

### 🤖 AI Service Assistant

- **HTMX Powered Chat**: Real-time conversational interface to help users find services.
- **Intelligent Discovery**: Ask the AI for professional recommendations based on your location and needs.

### 🛡️ Admin & Professional Management

- **Verification Pipeline**: Dedicated staff dashboard for vetting and approving service providers.
- **Job Lifecycle**: Full status tracking from 'Pending' through 'Accepted' and 'Completed'.

---

## 🛠️ Technology Stack

**Frontend**

- **Styling**: Custom Vanilla CSS3 (Glassmorphism & Desktop-First Responsive Design).
- **Framework**: Bootstrap 5 + Bootstrap Icons.
- **Interactivity**: JS (ES6+) & HTMX for asynchronous UI updates.
- **Mapping**: Leaflet.js + Leaflet Routing Machine.

**Backend**

- **Language**: Python 3.x
- **Framework**: Django 5.x / 6.x
- **Database**: SQLite/PostgreSQL (Django ORM).

---

## 📥 Installation & Setup

1. **Clone the repository**:

   ```bash
   git clone <repository-url>
   cd "local service"
   ```

2. **Create and Activate Virtual Environment**:

   ```bash
   python -m venv venv
   source venv/bin/activate  # Mac/Linux
   # venv\Scripts\activate  # Windows
   ```

3. **Install Dependencies**:

   ```bash
   pip install django pillow
   ```

4. **Run Migrations & Initialize**:

   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

5. **Start the Development Server**:
   ```bash
   python manage.py runserver
   ```
   _Dashboard will be active at `http://127.0.0.1:8000/`_

---

## 📂 Project Structure

- `services/`: Core application logic (Models, Views, HTML Templates).
- `media/`: Dynamic image storage for provider profiles and vetting documents.
- `config/`: Django project settings and global URL configurations.

---

## 🌟 Contributing

ServiceFinder is built with the **Antigravity Engineering Doctrine**: _Simplicity, Clarity, and Observability_. Every change must reduce friction and enhance the user experience.

---

© 2024 ServiceFinder. All Rights Reserved.
