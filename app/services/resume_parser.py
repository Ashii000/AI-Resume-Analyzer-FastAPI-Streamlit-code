"""Resume parsing utilities.

Lightweight parser that extracts contact details, experience years, education
snippets, and a skills list. Intended as a clear, testable starting point that
can be improved with spaCy and embedding-based matching later.
"""
from __future__ import annotations

import re
import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

# Default skills list; in production load from data/skills.csv or DB
DEFAULT_SKILLS = [
    "python",
    "sql",
    "machine learning",
    "fastapi",
    "docker",
    "aws",
    "git",
    "react",
    "excel",
    "power bi",
]


def _find_email(text: str) -> str:
    m = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
    return m.group(0) if m else ""


def _find_phone(text: str) -> str:
    m = re.search(r"(\+?\d[\d \-().]{6,}\d)", text)
    return m.group(0) if m else ""


def _find_name(text: str) -> str:
    # Heuristic: first non-empty line that is not contact info and shorter than 60 chars
    for line in text.splitlines():
        s = line.strip()
        if not s:
            continue
        if _find_email(s) or _find_phone(s):
            continue
        if len(s) <= 60 and any(c.isalpha() for c in s):
            return s
    return ""


def _extract_skills(text: str, skills_db: Optional[List[str]] = None) -> List[str]:
    text_low = text.lower()
    skills_db = skills_db or DEFAULT_SKILLS
    found = set()
    for skill in skills_db:
        if skill.lower() in text_low:
            found.add(skill)
    return sorted(found)


def _extract_experience_years(text: str) -> int:
    m = re.search(r"(\d+)\+?\s+years", text.lower())
    if m:
        try:
            return int(m.group(1))
        except ValueError:
            return 0
    return 0


def _extract_education(text: str) -> List[str]:
    education = []
    for line in text.splitlines():
        low = line.lower()
        if any(k in low for k in ["bsc", "bs ", "bachelor", "msc", "ms ", "master", "phd", "degree"]):
            education.append(line.strip())
    return education


def parse_resume_text(text: str, skills_db: Optional[List[str]] = None) -> Dict[str, Any]:
    """Parse resume text into structured data.

    Args:
        text: Raw extracted text from resume.
        skills_db: Optional list of skills to match against.

    Returns:
        Dict containing name, email, phone, skills, experience_years, education and a small raw snippet.
    """
    try:
        email = _find_email(text)
        phone = _find_phone(text)
        name = _find_name(text)
        skills = _extract_skills(text, skills_db)
        experience_years = _extract_experience_years(text)
        education = _extract_education(text)

        return {
            "name": name,
            "email": email,
            "phone": phone,
            "skills": skills,
            "experience_years": experience_years,
            "education": education,
            "raw_text_snippet": text[:500],
        }
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("Failed to parse resume text: %s", exc)
        return {"name": "", "email": "", "phone": "", "skills": [], "experience_years": 0, "education": [], "raw_text_snippet": text[:200]}
