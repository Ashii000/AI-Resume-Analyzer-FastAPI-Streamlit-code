"""PDF reading utilities.

Provides helpers to extract text and basic metadata from PDF bytes using
pdfplumber as the primary engine with PyMuPDF (fitz) as a fallback. Functions
are synchronous and intended to be called from FastAPI endpoints that read
file bytes first.
"""
from __future__ import annotations

import io
import logging
from typing import Dict, Tuple

logger = logging.getLogger(__name__)


def extract_text_and_meta(pdf_bytes: bytes) -> Tuple[str, Dict[str, object]]:
    """Extract text and metadata from PDF bytes.

    Tries pdfplumber first, then falls back to PyMuPDF (fitz). Returns a tuple
    of (extracted_text, metadata) where metadata can include page_count and
    author/title when available.

    Args:
        pdf_bytes: Raw PDF file bytes.

    Returns:
        A tuple (text, metadata).
    """
    text = ""
    meta: Dict[str, object] = {"page_count": 0}

    # Primary: pdfplumber
    try:
        import pdfplumber

        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            pages = [p.extract_text() or "" for p in pdf.pages]
            text = "\n".join(pages)
            meta["page_count"] = len(pdf.pages)
            # pdfplumber exposes simple metadata via pdf.metadata
            try:
                pdf_meta = pdf.metadata or {}
                if pdf_meta:
                    meta.update({"title": pdf_meta.get("Title"), "author": pdf_meta.get("Author")})
            except Exception:
                logger.debug("No PDF metadata available via pdfplumber")
        return text, meta
    except Exception as exc:  # fallback to PyMuPDF
        logger.debug("pdfplumber failed: %s", exc)

    try:
        import fitz  # PyMuPDF

        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        texts = []
        for page in doc:
            try:
                texts.append(page.get_text())
            except Exception:
                texts.append("")
        text = "\n".join(texts)
        meta["page_count"] = doc.page_count
        try:
            info = doc.metadata or {}
            meta.update({"title": info.get("title"), "author": info.get("author")})
        except Exception:
            logger.debug("No PDF metadata available via pymupdf")
        doc.close()
        return text, meta
    except Exception as exc:
        logger.exception("Failed to extract text from PDF: %s", exc)
        return "", meta
