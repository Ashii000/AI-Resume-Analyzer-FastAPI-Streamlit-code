"""Resume upload and parsing endpoints.

Features:
- Upload PDF or DOCX
- Validate file size and extension
- Extract text and metadata
- Persist file on disk and create Resume DB record
- Return parsed JSON metadata
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional, Dict, Any

from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config import settings
from app.database.database import get_db
from app.database import models
from app.services.pdf_reader import extract_text_and_meta as extract_pdf
from app.services.docx_reader import extract_text_and_meta as extract_docx
from app.services.resume_parser import parse_resume_text

logger = logging.getLogger(__name__)
router = APIRouter()

# Validation constants
ALLOWED_EXTENSIONS = {"pdf", "docx", "doc"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


def _secure_filename(original: str) -> str:
    """Return a safe filename by using a uuid prefix and preserving extension."""
    import uuid
    from pathlib import Path as _P

    ext = _P(original).suffix
    return f"{uuid.uuid4().hex}{ext}"


@router.post("/upload", status_code=201)
async def upload_resume(
    file: UploadFile = File(...),
    user_id: Optional[int] = Form(None),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Upload a resume (PDF/DOCX), parse it, store it, and return JSON metadata.

    Validates file type and size, extracts text, parses resume fields, stores the
    uploaded file on disk under settings.UPLOAD_DIR/resumes, and inserts a Resume
    record in the database with parsed_json.
    """
    filename = file.filename or "unnamed"
    ext = Path(filename).suffix.lower().lstrip(".")
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    content = await file.read()
    size = len(content)
    if size == 0:
        raise HTTPException(status_code=400, detail="Empty file")
    if size > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large")

    # Determine extraction method
    text = ""
    meta: Dict[str, Any] = {}
    try:
        if ext == "pdf":
            text, meta = extract_pdf(content)
        else:
            text, meta = extract_docx(content)
    except Exception as exc:
        logger.exception("Failed to extract text from file: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to process document")

    parsed = parse_resume_text(text)

    # Persist file to disk
    try:
        base = Path(settings.UPLOAD_DIR) / "resumes"
        base.mkdir(parents=True, exist_ok=True)
        stored_name = _secure_filename(filename)
        dest = base / stored_name
        dest.write_bytes(content)
    except Exception as exc:
        logger.exception("Failed to store uploaded file: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to store file")

    # Persist DB record
    try:
        # Store absolute resolved path for the stored file to avoid relative_path issues
        resume = models.Resume(user_id=user_id, filename=str(dest.resolve()), parsed_json={"parsed": parsed, "meta": meta})
        db.add(resume)
        db.commit()
        db.refresh(resume)
    except Exception as exc:
        logger.exception("Failed to create resume record: %s", exc)
        db.rollback()
        # Attempt to remove stored file on DB failure
        try:
            dest.unlink(missing_ok=True)
        except Exception:
            logger.debug("Failed to cleanup stored file after DB failure")
        raise HTTPException(status_code=500, detail="Failed to save resume record")

    return {"id": resume.id, "filename": resume.filename, "parsed": parsed, "meta": meta}


@router.get("/{resume_id}")
def get_resume(resume_id: int, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Return stored resume metadata and parsed JSON."""
    resume = db.get(models.Resume, resume_id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    return {"id": resume.id, "filename": resume.filename, "parsed": resume.parsed_json}
