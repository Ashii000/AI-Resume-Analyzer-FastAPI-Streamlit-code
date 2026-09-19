"""Job description parsing utilities.

Extracts structured fields from plain JD text such as skills, required
experience, degree requirements, and responsibilities. This module provides a
clear and testable starting point that can be improved with spaCy and
semantic extraction later.
"""
from __future__ import annotations

import re
import logging
from typing import Any, Dict, List, Optional

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
    "kubernetes",
    "rest api",
    "java",
]

DEGREE_KEYWORDS = ["bachelor", "bsc", "bs", "master", "msc", "phd", "degree"]


def _extract_skills(text: str, skills_db: Optional[List[str]] = None) -> List[str]:
    """Return a list of matching skills found in the text.

    Args:
        text: Raw text to search.
        skills_db: Optional list of skills to match; falls back to DEFAULT_SKILLS.
    """
    text_low = text.lower()
    skills_db = skills_db or DEFAULT_SKILLS
    found = set()
    for skill in skills_db:
        if skill.lower() in text_low:
            found.add(skill)
    return sorted(found)


def _extract_experience(text: str) -> int:
    """Extract years of experience requirement from text, if present.

    Returns the first integer found in patterns like `2+ years`, `3 years`, etc.
    """
    m = re.search(r"(\d+)\+?\s+years", text.lower())
    if m:
        try:
            return int(m.group(1))
        except ValueError:
            return 0
    # fallback: look for patterns like "minimum X years"
    m2 = re.search(r"minimum\s+(\d+)\s+years", text.lower())
    if m2:
        try:
            return int(m2.group(1))
        except ValueError:
            return 0
    return 0


def _extract_degrees(text: str) -> List[str]:
    """Identify degree requirements mentioned in the job description."""
    degrees = []
    for line in text.splitlines():
        low = line.lower()
        if any(k in low for k in DEGREE_KEYWORDS):
            degrees.append(line.strip())
    return degrees


def _extract_responsibilities(text: str) -> List[str]:
    """Extract a list of responsibilities from JD text.

    Strategy:
    - Look for a Responsibilities/Role/What you'll do section and capture following
      bullet lines until next blank line or section heading.
    - Fallback to capturing bullet lines anywhere in the document.
    """
    lines = text.splitlines()
    bullets = []

    # Search for header indices
    header_patterns = [r"responsibilit", r"responses?", r"what you'll do", r"role:", r"you will" ]
    start_idx = None
    for i, line in enumerate(lines):
        low = line.lower()
        if any(re.search(p, low) for p in header_patterns):
            start_idx = i + 1
            break

    if start_idx is not None:
        # collect bullets after header
        for line in lines[start_idx:]:
            if not line.strip():
                break
            if re.match(r"^\s*[-•·*]\s+", line) or line.strip().startswith("-"):
                bullets.append(line.strip().lstrip("-•·*").strip())
            else:
                # if it's an ordinary sentence, include as responsibility
                if len(line.strip()) > 20:
                    bullets.append(line.strip())
        if bullets:
            return bullets

    # fallback: capture any bullet points in the document
    for line in lines:
        if re.match(r"^\s*[-•·*]\s+", line) or line.strip().startswith("- "):
            bullets.append(line.strip().lstrip("-•·*").strip())

    return bullets


def parse_jd_text(text: str, skills_db: Optional[List[str]] = None) -> Dict[str, Any]:
    """Parse the job description text into structured data.

    Args:
        text: Raw job description text (string).
        skills_db: Optional list of skills to use for keyword matching.

    Returns:
        A dict with keys: skills (list), experience_years (int), degrees (list), responsibilities (list), title (optional)
    """
    try:
        skills = _extract_skills(text, skills_db)
        experience = _extract_experience(text)
        degrees = _extract_degrees(text)
        responsibilities = _extract_responsibilities(text)

        # Try to infer a title from the first line if it looks like one
        first_line = ""
        for ln in text.splitlines():
            s = ln.strip()
            if s:
                first_line = s
                break
        title = first_line if len(first_line) < 120 and len(first_line.split()) < 8 else None

        return {
            "title": title,
            "skills": skills,
            "experience_years": experience,
            "degrees": degrees,
            "responsibilities": responsibilities,
        }
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("Failed to parse job description: %s", exc)
        return {"title": None, "skills": [], "experience_years": 0, "degrees": [], "responsibilities": []}
