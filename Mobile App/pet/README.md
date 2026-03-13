# Pet Adoption Application Implementation

I have built the complete codebase for the Pet Adoption and Exchange platform.

## Architecture

- **Backend**: FastAPI (Python)
- **Database**: SQLite3
- **Frontend**: Flutter
- **Payments**: Razorpay
- **Maps**: Google Maps / Geolocator

### 📂 Backend
- `main.py`: Entry point.
- `models/`: DB models.
- `schemas/`: Pydantic validation.
- `routes/`: API endpoints.
- `services/`: Business logic.

### 📂 Frontend
- `lib/services/`: State management via Provider.
- `lib/screens/`: UI (Auth, Home, Pet Details, Add Pet, Profile).
- `lib/models/`: Data models.

## How to Run

### 1. Backend Setup
```bash
cd pet_adoption_backend
pip install fastapi uvicorn sqlalchemy passlib[bcrypt] python-jose[cryptography] python-multipart razorpay
python main.py
```

### 2. Frontend Setup
```bash
cd pet_adoption_app
flutter pub get
flutter run
```

> [!NOTE]
> Update `baseUrl` in `lib/config/api_config.dart` for emulator/physical devices.
