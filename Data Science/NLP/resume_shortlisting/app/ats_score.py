# ats/utils.py

import os
import re
import logging
import spacy
import pdfplumber
import docx
from rapidfuzz import fuzz, process
from collections import Counter


# Load Spacy NLP model
nlp = spacy.load("en_core_web_sm")

# ---------- File Text Extraction ----------
def extract_text(path: str) -> str:
    """Extract raw text from PDF, DOCX, or TXT files."""
    ext = os.path.splitext(path)[1].lower()
    logging.info(f"Extracting text from file: {path} (type: {ext})")

    if ext == ".pdf":
        text = ""
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                text += page_text + "\n"
        return text.strip()

    elif ext in (".docx",):
        doc = docx.Document(path)
        return "\n".join(p.text for p in doc.paragraphs if p.text.strip())

    elif ext == ".txt":
        return open(path, encoding="utf-8", errors="ignore").read()

    else:
        raise ValueError(f"Unsupported format: {ext}")


# ---------- NLP-based Extractors ----------
def extract_skills(text: str, jd_keywords=None) -> set:
    """Extract candidate skills from text and match against JD keywords if provided."""
    doc = nlp(text.lower())
    candidates = set()

    # Single tokens
    for token in doc:
        if token.pos_ in ["NOUN", "PROPN"] and not token.is_stop:
            candidates.add(token.lemma_.strip())

    # Multi-word noun chunks
    for chunk in doc.noun_chunks:
        candidates.add(chunk.lemma_.strip())

    # Match against JD keywords
    if jd_keywords:
        matched = set()
        for c in candidates:
            result = process.extractOne(c, jd_keywords, scorer=fuzz.token_sort_ratio)
            if result:
                match, score, _ = result
                if score > 85:
                    matched.add(match)
        return matched

    return candidates


def extract_education(text: str) -> list:
    """Extract institutions and degrees from resume text."""
    doc = nlp(text)
    results = []

    # Institutions
    for ent in doc.ents:
        if ent.label_ in ["ORG", "FAC"] and any(
            k in ent.text.lower()
            for k in ["university", "college", "institute", "school", "academy", "polytechnic"]
        ):
            results.append({"institution": ent.text})

    # Degrees
    degs = re.findall(
        r"(bachelor|master|phd|mba|b\.sc|m\.sc|ba|ma|ms|bs|btech|mtech)",
        text,
        flags=re.I,
    )
    for d in degs:
        results.append({"degree": d})

    return results


def extract_experience_years(text: str) -> int:
    """Extract maximum years of experience mentioned in text."""
    matches = re.findall(r"(\d+)\s*(?:\+|-)?\s*(years?|yrs?)", text, flags=re.I)
    if not matches:
        return 0
    years = [int(m[0]) for m in matches]
    return max(years)


def extract_jd_keywords(jd_text: str) -> set:
    """Extract important keywords from Job Description."""
    doc = nlp(jd_text.lower())
    tokens = [t.lemma_ for t in doc if t.is_alpha and not t.is_stop]
    freq = Counter(tokens)
    keywords = set([w for w, _ in freq.most_common(60)])

    # Remove generic/common words
    blacklist = {"team", "project", "work", "experience", "ability", "skill"}
    return {w for w in keywords if w not in blacklist}


# ---------- ATS Scoring ----------
def ats_score(resume_path: str, jd_text: str) -> float:
    """Takes a resume file path + JD text string, returns ATS result score (0-100)."""
    resume_text = extract_text(resume_path)

    # Keyword & Skills
    jd_keywords = extract_jd_keywords(jd_text)
    resume_skills = extract_skills(resume_text, jd_keywords)

    matched_keywords = resume_skills & jd_keywords
    keyword_score = len(matched_keywords) / len(jd_keywords) if jd_keywords else 0
    skill_score = len(matched_keywords) / (len(resume_skills) or 1)

    # Experience
    resume_years = extract_experience_years(resume_text)
    jd_years = extract_experience_years(jd_text)
    exp_score = min(1.0, resume_years / jd_years) if jd_years else (resume_years / 10.0)

    # Education
    resume_edu = extract_education(resume_text)
    edu_score = 0.0
    jd_lower = jd_text.lower()

    if "phd" in jd_lower:
        edu_score = 1.0 if any("phd" in str(e).lower() for e in resume_edu) else 0.0
    elif "master" in jd_lower:
        edu_score = 1.0 if any(
            "master" in str(e).lower() or "phd" in str(e).lower()
            for e in resume_edu
        ) else 0.0
    elif "bachelor" in jd_lower:
        edu_score = 1.0 if any(
            "bachelor" in str(e).lower()
            or "master" in str(e).lower()
            or "phd" in str(e).lower()
            for e in resume_edu
        ) else 0.0
    elif resume_edu:
        edu_score = 0.8

    # Weighted Overall Score
    overall = (
        0.5 * skill_score +
        0.3 * exp_score +
        0.2 * edu_score
    )



    return round(overall * 100, 1)
