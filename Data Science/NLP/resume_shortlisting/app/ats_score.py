# ats/utils.py

import os
import re
import spacy
import pdfplumber
import docx
from rapidfuzz import fuzz, process
from collections import Counter

nlp = spacy.load("en_core_web_sm")

# ---------- File Text Extraction ----------
def extract_text(path):
    ext = os.path.splitext(path)[1].lower()
    print(ext)
    print(ext)
    if ext == ".pdf":
        text = ""
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
        return text
    elif ext in (".docx", ".doc"):
        doc = docx.Document(path)
        return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    elif ext == ".txt":
        return open(path, encoding="utf-8", errors="ignore").read()
    else:
        raise ValueError(f"Unsupported format: {ext}")


# ---------- NLP-based Extractors ----------
def extract_skills(text, jd_keywords=None):
    doc = nlp(text.lower())
    candidates = set()

    for token in doc:
        if token.pos_ in ["NOUN", "PROPN"] and not token.is_stop:
            candidates.add(token.lemma_.strip())

    if jd_keywords:
        matched = set()
        for c in candidates:
            result = process.extractOne(c, jd_keywords, scorer=fuzz.QRatio)
            if result:
                match, score, _ = result
                if score > 85:
                    matched.add(match)
        return matched
    return candidates



def extract_education(text):
    doc = nlp(text)
    results = []
    for ent in doc.ents:
        if ent.label_ in ["ORG", "FAC"] and any(k in ent.text.lower() for k in ["university","college","institute","school"]):
            results.append({"institution": ent.text})
    degs = re.findall(r"(bachelor|master|phd|mba)", text, flags=re.I)
    for d in degs:
        results.append({"degree": d})
    return results


def extract_experience_years(text):
    matches = re.findall(r"(\d+)\+?\s+years?", text, flags=re.I)
    return max(map(int, matches)) if matches else 0


def extract_jd_keywords(jd_text):
    doc = nlp(jd_text.lower())
    tokens = [t.lemma_ for t in doc if t.is_alpha and not t.is_stop]
    freq = Counter(tokens)
    return set([w for w, _ in freq.most_common(60)])


# ---------- ATS Scoring ----------
def ats_score(resume_path, jd_text):
    """Takes a resume file path + JD text string, returns ATS result dict."""
    resume_text = extract_text(resume_path)
    

    jd_keywords = extract_jd_keywords(jd_text)
    resume_skills = extract_skills(resume_text, jd_keywords)

    matched_keywords = resume_skills & jd_keywords
    keyword_score = len(matched_keywords) / len(jd_keywords) if jd_keywords else 0
    skill_score = len(matched_keywords) / (len(resume_skills) or 1)

    resume_years = extract_experience_years(resume_text)
    jd_years = extract_experience_years(jd_text)
    exp_score = min(1.0, resume_years / jd_years) if jd_years else (resume_years / 10.0)

    resume_edu = extract_education(resume_text)
    edu_score = 0.8 if resume_edu else 0.0
    if "bachelor" in jd_text.lower():
        edu_score = 1.0 if any("bachelor" in str(e).lower() for e in resume_edu) else 0.0
    if "master" in jd_text.lower():
        edu_score = 1.0 if any("master" in str(e).lower() for e in resume_edu) else 0.0

    print(edu_score)
    print(skill_score)
    print(exp_score)
    overall = (
        0.5 * skill_score +
        0.3 * exp_score +
        0.2 * edu_score
    )
    print("Overall Score:", overall)

    return round(overall * 100, 1)