import os
import re
import logging
import pdfplumber
import docx
import ollama
import json
from .models import JobSeekerProfile, JobPost

# ---------- File Text Extraction ----------
def extract_text(path: str) -> str:
    """Extract raw text from PDF, DOCX, or TXT files."""
    ext = os.path.splitext(path)[1].lower()
    logging.info(f"Extracting text from file: {path} (type: {ext})")

    try:
        if ext == ".pdf":
            text = ""
            with pdfplumber.open(path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text() or ""
                    text += page_text + "\n"
            return text.strip()

        elif ext == ".docx":
            doc = docx.Document(path)
            return "\n".join(p.text for p in doc.paragraphs if p.text.strip())

        elif ext == ".txt":
            with open(path, encoding="utf-8", errors="ignore") as f:
                return f.read()

        else:
            raise ValueError(f"Unsupported format: {ext}")
    except Exception as e:
        logging.error(f"Error extracting text from {path}: {e}")
        return ""


# ---------- ATS Scoring with Ollama ----------
def ats_score(resume_path: str, job_seeker_profile: JobSeekerProfile, job_post: JobPost) -> float:
    """
    Completely uses Ollama (qwen3-vl:235b-cloud) to extract data and predict the ATS score.
    """
    try:
        # 1. Extract raw text from the document
        resume_text = extract_text(resume_path)
        if not resume_text:
            logging.warning("No text extracted from resume.")
            return 0.0

        # 2. Prepare job details
        jd_details = {
            "title": job_post.job_title,
            "company": job_post.company,
            "description": job_post.description,
            "required_skills": job_post.skills, # Assuming this is a list or string
            "required_experience": job_post.experience,
            "salary": job_post.salary,
            "location": job_post.location
        }

        # 3. Construct the comprehensive prompt for Ollama
        prompt = f"""
        You are an advanced AI Recruitment Specialist and ATS Analyzer.
        Your task is to analyze a candidate's resume against a specific Job Description (JD).
        
        ### STEP 1: Extract Key Information from Resume
        Extract skills, experience years, education, and relevant projects from the following resume text.
        
        ### STEP 2: Compare with Job Description
        Compare the extracted candidate data with the JD provided below.
        
        ### STEP 3: Calculate ATS Score
        Determine an ATS compatibility score (0-100) based on:
        - Skill Matching (40%): How well the technical and soft skills align.
        - Experience Relevancy (30%): Years and quality of relevant work history.
        - Education & Certification (15%): Academic requirements and professional certs.
        - Overall Fit (15%): Location, industry fit, and job-specific nuances.

        --- 
        RESUME TEXT:
        {resume_text}
        ---
        JOB DESCRIPTION:
        {json.dumps(jd_details, indent=2)}
        ---

        ### OUTPUT INSTRUCTIONS:
        Return ONLY a JSON object. No other text. The JSON must have this structure:
        {{
            "extracted_data": {{
                "skills": [],
                "total_years_experience": 0,
                "education": []
            }},
            "analysis": {{
                "skill_match_score": 0,
                "experience_match_score": 0,
                "strengths": [],
                "weaknesses": []
            }},
            "ats_score": <final_score_number>
        }}
        """

        # 4. Call Ollama model
        response = ollama.generate(
            model='qwen3-vl:235b-cloud',
            prompt=prompt,
            options={
                "temperature": 0.2, # Lower temperature for more consistent scoring
            }
        )
        
        response_text = response.get('response', '').strip()
        logging.info(f"Ollama Response: {response_text[:200]}...") # Log start of response

        # 5. Parse JSON and return score
        try:
            # Handle potential markdown formatting in response
            clean_json = re.search(r'\{.*\}', response_text, re.DOTALL)
            if clean_json:
                data = json.loads(clean_json.group(0))
                score = data.get('ats_score', 0)
                # Ensure score is a float and within 0-100
                return min(max(float(score), 0.0), 100.0)
        except Exception as json_err:
            logging.error(f"Failed to parse Ollama JSON: {json_err}")
            # Fallback: simple numeric extraction
            numeric_match = re.search(r'"ats_score":\s*(\d+\.?\d*)', response_text)
            if numeric_match:
                return float(numeric_match.group(1))
        
        return 0.0

    except Exception as e:
        logging.error(f"Critical error in ats_score process: {e}")
        return 0.0
