# 🛠️ ServiceFinder: Next-Gen AI-Powered Services Marketplace

ServiceFinder is a high-performance, intelligent platform designed to bridge the gap between local service professionals and clients. It leverages local AI (Ollama/DeepSeek) and geographical intelligence to provide a seamless, high-trust marketplace experience.

---

## 🌟 Core Features

### 🧠 1. Intelligent Ranking Engine
Unlike traditional platforms that rely solely on ratings, ServiceFinder uses a **normalized multi-factor scoring algorithm** to rank professionals:
- **Rating (35%)**: Aggregated user feedback.
- **Completion Rate (25%)**: Ratio of successful jobs to cancellations.
- **Punctuality (20%)**: Based on "on-time" review data.
- **Proximity (10%)**: Distance-weighted score using the Haversine formula.
- **Response Speed (10%)**: Avg. time taken to accept or acknowledge requests.

### 💬 2. Decision-Support AI Chatbot
A real-time assistant built with **HTMX** and powered by **Ollama (DeepSeek)**:
- **Natural Language Parsing**: Identify categories, locations, and budgets from messages like *"Need a cheap plumber in Mumbai завтра."*
- **Dynamic Recommendations**: Recommends top-ranked professionals directly within the chat.
- **Multilingual Support**: Fully localized interactions in **English** and **Tamil (தமிழ்)**.

### 📍 3. Geographical Intelligence
- **Real-time GPS Tracking**: Detects user location via HTML5 Geolocation API for immediate "near me" results.
- **AI Geocoding**: Integrated with **OpenCage API** to convert raw addresses into precise coordinates.
- **Area-Based Filtering**: Smart 50km radius logic ensures you only see pros who can actually reach you.

### 📅 4. High-Trust Booking Workflow
- **Integrated Booking System**: Request appointments with specific time slots.
- **Status Management**: Real-time status updates (Pending → Accepted → Completed).
- **Notification System**: Instant alerts for booking changes and system updates.
- **Cost Estimation**: Dynamic pricing preview based on duration and professional rates.

---

## 🏗️ Tech Stack

- **Backend**: Django 5.2 (Python)
- **Frontend**: Vanilla CSS, Bootstrap Icons, HTMX (for dynamic chat & updates)
- **AI/LLM**: Ollama (DeepSeek-v3.1)
- **Geocoding**: OpenCage Geocode API
- **Database**: SQLite (Development) / PostgreSQL (Production ready)

---

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.10+
- [Ollama](https://ollama.ai/) installed locally
- OpenCage API Key

### 2. Installation
```bash
# Clone the repository
git clone <repo-url>
cd local-service

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Setup
Create or update `config/settings.py` with your credentials:
```python
OPENCAGE_API_KEY = 'your_api_key_here'
OLLAMA_BASE_URL = 'http://localhost:11434'
OLLAMA_MODEL = 'deepseek-v3.1:671b-cloud'
```

### 4. Database Setup
```bash
python manage.py migrate
# Seed initial categories and professionals
# (Run your seeding script if available, e.g., seed_experts.py)
```

### 5. Run the Server
```bash
python manage.py runserver
```

---

## 📂 Project Structure

- `services/`: Core application containing models, views, and AI logic.
  - `intelligence.py`: The "brain" — Ranking scoring, Haversine distance, and Geocoding.
  - `views.py`: Logic for search, chat, and booking workflows.
  - `models.py`: Database schema for Users, Pros, Bookings, and Reviews.
- `config/`: Project settings and URL routing.
- `templates/`: Premium, responsive layouts using native CSS and Bootstrap components.

---

## 🛡️ Trust & Security
- **Dual Dashboards**: Separate tailored experiences for Clients and Professionals.
- **Review Verification**: Reviews can only be submitted for completed bookings.
- **Private Profiles**: User location and preferences are securely handled.

---

*Developed with ❤️ as an elite local services solution.*
