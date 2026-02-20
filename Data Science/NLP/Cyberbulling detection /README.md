# Cyberbullying Detection System

A machine learning-powered web application designed to identify and classify cyberbullying in text content. Built with **Django** and **Scikit-learn**, the system provides a real-time prediction interface with user authentication for secure access.

## 🚀 Features

-   **Cyberbullying Classification**: Uses a trained Logistic Regression model to detect offensive or bullying content.
-   **High Accuracy**: Achieves approximately **88% accuracy** on the test dataset.
-   **User Authentication**: Secure registration, login, and logout functionality.
-   **Text Preprocessing**: Robust NLP pipeline using NLTK (lemmatization, stopword removal, and cleaning).
-   **Premium UI**: Sleek and modern web interface with a responsive design.

## 🛠️ Technology Stack

-   **Machine Learning**: Python, Scikit-learn, Pandas, Joblib.
-   **NLP**: NLTK (Natural Language Toolkit).
-   **Web Framework**: Django.
-   **Frontend**: HTML5, CSS3, Vanilla JavaScript.
-   **Data Storage**: SQLite (Default Django DB).

## 📊 Model Details

-   **Algorithm**: Logistic Regression.
-   **Vectorization**: TF-IDF Vectorizer (Max features: 50,000, N-gram range: 1-2).
-   **Accuracy**: 88.35%
-   **Dataset**: HuggingFace dataset (Parquet format).

### Classification Report:
| Class | Precision | Recall | F1-Score |
| :--- | :--- | :--- | :--- |
| **Not Cyberbullying** | 0.87 | 0.90 | 0.89 |
| **Cyberbullying** | 0.90 | 0.86 | 0.88 |

## 📁 Project Structure

```text
.
├── Untitled-1.ipynb        # Model training and evaluation notebook
├── train-00000-of-0...      # Dataset in parquet format
├── nltk_data/               # Pre-downloaded NLTK resources
├── website/                 # Django web application
│   ├── manage.py            # Django management script
│   ├── app/                 # Main application logic (views, urls)
│   │   ├── templates/       # HTML templates
│   │   └── views.py         # Prediction and authentication logic
│   └── static/
│       ├── models/          # Exported .pkl model and vectorizer
│       └── bg.png           # UI assets
└── .venv/                   # Python virtual environment
```

## ⚙️ Setup & Installation

### 1. Clone the repository
```bash
git clone <repository-url>
cd "Cyberbulling detection "
```

### 2. Create and Activate Virtual Environment
```bash
python -m venv .venv
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```
*(Note: If requirements.txt is missing, install: django, scikit-learn, joblib, nltk, pandas, pyarrow)*

### 4. Setup NLTK Data
The project includes an `nltk_data` folder. The application is configured to look for NLTK data in this local directory.

### 5. Run the Server
```bash
cd website
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

### 6. Access the App
Open your browser and navigate to `http://127.0.0.1:8000/`.

## 🖥️ Usage

1.  **Register/Login**: Create an account or sign in to access the predictor.
2.  **Predict**: Navigate to the prediction page, enter the text you want to analyze, and click "Predict".
3.  **Result**: The system will display whether the text is classified as "Cyberbullying" or "Not Cyberbullying".

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License.
