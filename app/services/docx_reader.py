"""DOCX reading utilities.

Extracts text from docx bytes using python-docx. Returns extracted text and
basic metadata (e.g., paragraph count).
"""
from __future__ import annotations

import io
import logging
from typing import Dict, Tuple

logger = logging.getLogger(__name__)


def extract_text_and_meta(docx_bytes: bytes) -> Tuple[str, Dict[str, object]]:
    """Extract text and metadata from DOCX bytes.

    Args:
        docx_bytes: Raw DOCX file bytes.

    Returns:
        Tuple of (text, metadata)
    """
    text = ""
    meta: Dict[str, object] = {"paragraph_count": 0}
    try:
        import docx

        doc = docx.Document(io.BytesIO(docx_bytes))
        paragraphs = [p.text for p in doc.paragraphs if p.text]
        text = "\n".join(paragraphs)
        meta["paragraph_count"] = len(paragraphs)
        return text, meta
    except Exception as exc:
        logger.exception("Failed to extract DOCX text: %s", exc)
        return "", meta
