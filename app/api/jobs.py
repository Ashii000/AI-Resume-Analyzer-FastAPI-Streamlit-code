"""Job Description API endpoints.

Provides endpoints to create job descriptions by pasting text or uploading
PDF/DOCX files. Extracts skills, experience, degree requirements, and
responsibilities, persists the job record, and returns structured JSON.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config import settings
from app.database.database import get_db
from app.database import models
from app.services.pdf_reader import extract_text_and_meta as extract_pdf
from app.services.docx_reader import extract_text_and_meta as extract_docx
from app.services.jd_parser import parse_jd_text

logger = logging.getLogger(__name__)
router = APIRouter()

ALLOWED_EXTENSIONS = {"pdf", "docx", "doc"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


def _secure_filename(original: str) -> str:
    """Generate a secure filename preserving the original extension.

    Args:
        original: Original filename provided by the uploader.

    Returns:
        A filename with a uuid4 hex prefix and original extension.
    """
    import uuid
    from pathlib import Path as _P

    ext = _P(original).suffix
    return f"{uuid.uuid4().hex}{ext}"


@router.post("/upload", status_code=201)
async def upload_job(
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Upload a job description file (PDF/DOCX), extract and persist parsed data.

    Returns the created Job record ID and parsed JSON.
    """
    filename = file.filename or "unnamed"
    ext = Path(filename).suffix.lower().lstrip(".")
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty file")
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large")

    try:
        if ext == "pdf":
            text, meta = extract_pdf(content)
        else:
            text, meta = extract_docx(content)
    except Exception as exc:
        logger.exception("Failed to extract job description: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to process document")

    parsed = parse_jd_text(text)

    # Persist file to disk
    try:
        base = Path(settings.UPLOAD_DIR) / "jobs"
        base.mkdir(parents=True, exist_ok=True)
        stored_name = _secure_filename(filename)
        dest = base / stored_name
        dest.write_bytes(content)
    except Exception as exc:
        logger.exception("Failed to store job file: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to store file")

    # Persist DB record
    try:
        # Store absolute resolved path for the stored job file
        job = models.Job(title=title or parsed.get("title"), original_text=text, parsed_json={"parsed": parsed, "meta": meta})
        db.add(job)
        db.commit()
        db.refresh(job)
    except Exception as exc:
        logger.exception("Failed to create job record: %s", exc)
        db.rollback()
        try:
            dest.unlink(missing_ok=True)
        except Exception:
            logger.debug("Failed to cleanup stored job file after DB failure")
        raise HTTPException(status_code=500, detail="Failed to save job record")

    return {"id": job.id, "title": job.title, "parsed": parsed, "meta": meta}


@router.post("/paste", status_code=201)
def paste_job(
    text: str = Form(...), title: Optional[str] = Form(None), db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Accept a pasted job description text, parse and persist it."""
    if not text or not text.strip():
        raise HTTPException(status_code=400, detail="Empty job description")

    parsed = parse_jd_text(text)

    try:
        job = models.Job(title=title or parsed.get("title"), original_text=text, parsed_json={"parsed": parsed, "meta": {}})
        db.add(job)
        db.commit()
        db.refresh(job)
    except Exception as exc:
        logger.exception("Failed to create job record from pasted text: %s", exc)
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to save job record")

    return {"id": job.id, "title": job.title, "parsed": parsed}


@router.get("/{job_id}")
def get_job(job_id: int, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Retrieve a stored job record and its parsed data."""
    job = db.get(models.Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"id": job.id, "title": job.title, "parsed": job.parsed_json}
