# AQI Prediction System

A modern, full-stack web application designed to predict the Air Quality Index (AQI) based on various atmospheric pollutant levels. Built with Flask and powered by a Random Forest machine learning model.

## 🌟 Features

- **User Authentication**: Secure registration and login system.
- **AQI Prediction**: Predict air quality categories (Good, Moderate, Poor, etc.) using real-time pollutant data.
- **Pollutants Tracked**:
  - PM2.5 & PM10
  - NO, NO2 & NH3
  - CO, SO2 & O3
  - Benzene, Toluene & Xylene
- **Prediction History**: Logged-in users can view their past 10 predictions.
- **RESTful API**: Integration-ready API endpoint for automated predictions.
- **Responsive Design**: Clean and intuitive user interface built with Jinja2 templates.

## 🛠️ Tech Stack

- **Backend**: [Flask](https://flask.palletsprojects.com/) (Python)
- **Database**: [SQLAlchemy](https://www.sqlalchemy.org/) (SQLite)
- **Authentication**: Flask-Login
- **Machine Learning**: [Scikit-learn](https://scikit-learn.org/), Pandas, Joblib
- **Forms**: Flask-WTF & WTForms
- **Frontend**: HTML5, Vanilla CSS, Jinja2

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- pip (Python package manager)

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd website
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Setup**:
   Create a `.env` file in the root directory (optional, but recommended for production):
   ```env
   SECRET_KEY=your-secret-key-here
   ```

### Running the Application

1. Start the Flask server:
   ```bash
   python app.py
   ```
2. Open your browser and navigate to `http://localhost:8000`.

## 📂 Project Structure

- `app.py`: Main application logic, routes, and database models.
- `models/`: Contains the pre-trained Random Forest model (`rf_aqi_model.pkl`).
- `templates/`: HTML templates for the application pages.
- `requirements.txt`: List of Python dependencies.
- `instance/`: SQLite database storage.

## 🍎 API Usage

To get predictions via the API, send a POST request to `/api/predict`:

**Endpoint**: `POST /api/predict`  
**Payload**:
```json
{
  "pm25": 45.0,
  "pm10": 80.0,
  "no": 1.2,
  "no2": 15.0,
  "nh3": 5.0,
  "co": 0.8,
  "so2": 4.5,
  "o3": 25.0,
  "benzene": 0.5,
  "toluene": 1.2,
  "xylene": 0.3
}
```

## 📝 License

This project is licensed under the MIT License.
