"""
ATS Resume Scanner - Core Logic
--------------------------------
Extracts text from a resume PDF, extracts skills from both the resume
and a job description, and computes a match score with feedback.

Usage:
    python3 scanner.py <resume.pdf> <job_description.txt>
"""

import sys
import re
import pdfplumber
from skills_data import SKILLS_TAXONOMY


# ---------- Step 1: PDF Text Extraction ----------

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract raw text from a PDF resume."""
    text_parts = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
    return "\n".join(text_parts)


# ---------- Step 2: Skill Extraction ----------

def extract_skills(text: str) -> set:
    """
    Find which known skills (from SKILLS_TAXONOMY) appear in the given text.
    Case-insensitive, handles multi-word skills like 'machine learning'.
    """
    text_lower = text.lower()
    found = set()
    for skill in SKILLS_TAXONOMY:
        # word-boundary-safe search, handles skills with symbols like c++, c#
        pattern = re.escape(skill)
        if re.search(rf"(?<!\w){pattern}(?!\w)", text_lower):
            found.add(skill)
    return found


# ---------- Step 3: Scoring ----------

def compute_score(resume_skills: set, jd_skills: set) -> dict:
    """
    Simple keyword-overlap scoring:
    score = (matched skills) / (total required skills in JD) * 100
    """
    if not jd_skills:
        return {"score": 0, "matched": [], "missing": []}

    matched = sorted(resume_skills & jd_skills)
    missing = sorted(jd_skills - resume_skills)
    score = round(len(matched) / len(jd_skills) * 100, 1)

    return {"score": score, "matched": matched, "missing": missing}


# ---------- Step 4: Formatting Checks (basic ATS pitfalls) ----------

def check_formatting_flags(pdf_path: str) -> list:
    """Flag common ATS-unfriendly formatting issues."""
    flags = []
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            if page.extract_tables():
                flags.append(f"Page {i+1} contains a table — some ATS parsers misread tabular layouts.")
            if page.images:
                flags.append(f"Page {i+1} contains image(s) — text inside images won't be read by most ATS.")
    return flags


# ---------- Main ----------

def run_scan(resume_pdf_path: str, jd_text_path: str):
    resume_text = extract_text_from_pdf(resume_pdf_path)
    with open(jd_text_path, "r", encoding="utf-8") as f:
        jd_text = f.read()

    resume_skills = extract_skills(resume_text)
    jd_skills = extract_skills(jd_text)

    result = compute_score(resume_skills, jd_skills)
    flags = check_formatting_flags(resume_pdf_path)

    print("=" * 50)
    print("ATS RESUME SCAN RESULT")
    print("=" * 50)
    print(f"Match Score: {result['score']}%\n")
    print(f"Matched Skills ({len(result['matched'])}):")
    print(", ".join(result['matched']) if result['matched'] else "  none")
    print(f"\nMissing Skills ({len(result['missing'])}):")
    print(", ".join(result['missing']) if result['missing'] else "  none")

    if flags:
        print("\nFormatting Warnings:")
        for f in flags:
            print(f"  - {f}")

    return result


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 scanner.py <resume.pdf> <job_description.txt>")
        sys.exit(1)
    run_scan(sys.argv[1], sys.argv[2])
