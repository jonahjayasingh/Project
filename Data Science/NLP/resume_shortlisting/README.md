# AI-Powered ATS Resume Shortlisting System

An advanced Applicant Tracking System (ATS) that leverages Artificial Intelligence to score and rank resumes against job descriptions. Built with Django and powered by Ollama's Large Language Models (LLM), this system helps recruiters identify the most qualified candidates efficiently.

## 🚀 Key Features

### 🏢 For Companies / Recruiters
- **Job Management**: Create, edit, and manage job postings with specific skill requirements and experience levels.
- **Smart Shortlisting**: Automatically rank applicants based on an AI-calculated ATS score (0-100).
- **Applicant Analytics**: View detailed analysis of candidate strengths and weaknesses relative to the job description.
- **Dynamic Status**: Toggle job postings between active and inactive states.

### 👤 For Job Seekers
- **Personalized Dashboard**: Browse active job opportunities filtered by title, type, and experience.
- **Easy Application**: Apply to jobs by uploading resumes in PDF, DOCX, or TXT formats.
- **Profile Management**: Maintain a professional profile with contact details and a profile picture.
- **Instant Confirmation**: Receive automated email notifications upon successful application.

### 🤖 AI Scoring Engine
- Uses **Ollama (Qwen model)** to perform deep semantic analysis.
- Evaluates candidates across multiple dimensions:
  - **Skill Match (40%)**: Alignment of technical and soft skills.
  - **Experience Relevancy (30%)**: Quality and duration of work history.
  - **Education (15%)**: Academic background and certifications.
  - **Overall Fit (15%)**: Industry relevance and specific nuances.

## 🛠️ Tech Stack
- **Framework**: Django (Python)
- **AI/LLM**: Ollama (Qwen3-VL)
- **Document Processing**: `pdfplumber`, `python-docx`
- **Database**: SQLite (Default)
- **Styling**: Modern, responsive UI with CSS

## 📋 Prerequisites
- Python 3.10+
- Django 5.0+
- [Ollama](https://ollama.com/) installed and running locally.

## ⚙️ Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd resume_shortlisting
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Ollama**:
   Ensure Ollama is running and pull the required model (if using a specific one, or adjust `ats_score.py` to your preferred model):
   ```bash
   ollama pull qwen
   ```

4. **Run migrations**:
   ```bash
   python manage.py migrate
   ```

5. **Start the development server**:
   ```bash
   python manage.py runserver
   ```

6. **Access the application**:
   Open `http://127.0.0.1:8000` in your browser.

## 📧 Email Configuration
To enable application confirmation emails, update the `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD` settings in `resume_shortlisting/settings.py` (or configure a custom SMTP server in `app/custom_email.py`).

## 📁 Project Structure
- `app/`: Core application logic, views, and models.
- `app/ats_score.py`: AI scoring logic and file extraction.
- `media/`: Storage for uploaded resumes and profile pictures.
- `templates/`: HTML templates for the web interface.

## 🤝 Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

---
*Created with ❤️ by the AI Recruitment Team*
