# 🚥 TrafficSign AI: Intelligent Indian Traffic Sign Detection

TrafficSign AI is a state-of-the-art computer vision application designed to identify and categorize Indian road signs in real-time. Built with **Django**, **YOLOv8**, and **OpenCV**, it provides a seamless interface for both static image analysis and live camera streams.

---

## 🌟 Key Features

- **🚀 Real-Time Live Detection**: Instant traffic sign identification from your camera using an optimized OpenCV-based frame processing pipeline.
- **🖼️ Static Image Analysis**: Upload images to get detailed detection reports, including cropped views of each identified sign.
- **🎯 High Accuracy**: Leverages a custom-trained YOLOv8 model specifically optimized for Indian road sign variations.
- **💎 Modern UI/UX**: Features a sleek, responsive dashboard designed with Glassmorphism aesthetics and smooth animations.
- **🔒 Secure Authentication**: Integrated user registration and login system to protect and personalize the experience.
- **⚡ Performance Optimized**: Minimal latency achieved through efficient frame encoding and light-weight inference.

---

## 🛠️ Technology Stack

| Layer | Technology |
| :--- | :--- |
| **Backend** | Django (Python 3.x) |
| **AI Engine** | YOLOv8 (Ultralytics) |
| **Computer Vision** | OpenCV (`cv2`) |
| **Frontend** | Vanilla CSS, JavaScript (ES6+), HTML5 |
| **Database** | SQLite3 (Default) |
| **Image Handling** | NumPy, Base64 encoding |

---

## 📂 Project Structure

```text
Traffic sign detection/
├── README.md                # Project documentation
├── Website/                 # Main Django project directory
│   ├── core/                # Core application logic (Views, URLs, Models)
│   ├── templates/           # HTML templates (Glassmorphism design)
│   ├── static/              # CSS, JS, and image assets
│   ├── model/               # YOLOv8 weight files (best.pt)
│   ├── media/               # Processed results and temporary storage
│   └── manage.py            # Django management script
└── Indian-Traffic-Sign-1/   # Dataset and training metadata (optional)
```

---

## ⚙️ Installation & Setup

1. **Clone the Project**
   ```bash
   git clone [your-repository-url]
   cd "Traffic sign detection"
   ```

2. **Create a Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install django opencv-python ultralytics numpy
   ```

4. **Initialize Database**
   ```bash
   cd Website
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Run the Server**
   ```bash
   python manage.py runserver
   ```
   Access the app at `http://127.0.0.1:8000`

---

## 📖 How to Use

### 1. Account Creation
Users must **Register** or **Login** to access the detection features.

### 2. Image Prediction
- Navigate to "Get Started" from the home page.
- Upload any image containing Indian traffic signs.
- The system will process the image and display it with bounding boxes, labels, and confidence scores.
- Individually cropped signs are shown below the main result for clarity.

### 3. Live Detection
- Click "Live Camera" in the dashboard.
- Grant camera permissions to the browser.
- The system will start a real-time loop, capturing frames and sending them to the Django backend for processing via OpenCV.
- Detected signs appear dynamically with smooth visual feedback.

---

## 📊 Model Performance
The system uses a **YOLOv8** model trained on a curated dataset of Indian traffic signs, achieving high precision even in variable lighting and weather conditions.
- **mAP@50**: ~92%
- **Inference Speed**: ~20-30ms (CPU-bound)
- **Supported Classes**: Speed limit, No Entry, Turn signals, Stop signs, etc.

---
*Developed for intelligent transportation systems and road safety awareness.*
