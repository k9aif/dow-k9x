# SPDX-License-Identifier: Apache-2.0
# K9-AIF Framework
"""Stage NORMALIZE (process model mca-2026-10): any upload becomes Markdown.

Text and Markdown files are read as they are. PDF, Word, PowerPoint, Excel,
HTML and images go through the framework's DoclingParser (Docling-Serve at
DOCLING_ENDPOINT: layout analysis, tables, OCR for scanned pages). The original
file is kept in object storage beside the job's stage results, so a reviewer can
always compare the Markdown the agents read with what was submitted.

A conversion that fails or yields no text stops the upload with a reason; DAS
never runs the pipeline on a garbled byte decode of a binary file.
"""

from __future__ import annotations

import logging
import tempfile
from pathlib import Path
from typing import Any, Dict, Optional

from k9_dow.config.settings import settings

log = logging.getLogger(__name__)

TEXT_SUFFIXES = {".md", ".markdown", ".txt"}
DOCLING_SUFFIXES = {".pdf", ".docx", ".pptx", ".xlsx", ".html", ".htm",
                    ".png", ".jpg", ".jpeg", ".tif", ".tiff"}
MAX_UPLOAD_BYTES = 25 * 1024 * 1024
ORIGINALS_BUCKET = "jcids-output"


class NormalizationError(ValueError):
    """The upload can't be turned into text; the message is shown to the user."""


def accepted_suffixes() -> list:
    return sorted(TEXT_SUFFIXES | DOCLING_SUFFIXES)


def normalize_upload(config: Dict[str, Any], filename: str, content: bytes) -> Dict[str, Any]:
    """Return ``{"markdown", "method", "chars", "seconds"}`` for an uploaded file."""
    if len(content) > MAX_UPLOAD_BYTES:
        raise NormalizationError(f"File is {len(content) // (1024 * 1024)} MB; the limit is 25 MB.")
    suffix = Path(filename).suffix.lower()
    if suffix in TEXT_SUFFIXES:
        text = content.decode("utf-8", errors="replace")
        if not text.strip():
            raise NormalizationError("The file has no text.")
        return {"markdown": text, "method": "text", "chars": len(text), "seconds": 0.0}
    if suffix not in DOCLING_SUFFIXES:
        raise NormalizationError(
            f"Unsupported file type '{suffix or filename}'. Accepted: {', '.join(accepted_suffixes())}.")

    from k9_aif_abb.k9_agents.retrieval.docling_parser import DoclingParser

    parser = DoclingParser(config=config, url=settings.DOCLING_ENDPOINT)
    with tempfile.TemporaryDirectory(prefix="das-upload-") as tmp:
        path = Path(tmp) / Path(filename).name
        path.write_bytes(content)
        result = parser.execute({"path": str(path), "filename": filename})
    if result.get("status") != "ok":
        log.warning("[Normalize] Docling failed for %s: %s", filename, result.get("error"))
        raise NormalizationError(
            "The document could not be converted to text (Docling: "
            f"{result.get('status')}). Try again, or upload a Markdown or text version.")
    md = result["markdown"]
    log.info("[Normalize] %s -> %d chars via Docling in %ss", filename, len(md), result.get("seconds"))
    return {"markdown": md, "method": "docling", "chars": len(md), "seconds": result.get("seconds")}


def save_original(config: Dict[str, Any], job_id: str, filename: str, content: bytes) -> Optional[str]:
    """Keep the submitted file; returns its object-storage URI (None if storage is down)."""
    try:
        from k9_aif_abb.k9_factories.object_storage_factory import ObjectStorageFactory
        store = ObjectStorageFactory.create(config)
        from k9_dow.config.instance import key_prefix
        key = f"{key_prefix()}by-job/{job_id}/original/{Path(filename).name}"
        store.upload(ORIGINALS_BUCKET, key, content)
        return store.get_uri(ORIGINALS_BUCKET, key)
    except Exception as exc:
        log.warning("[Normalize] keeping the original for job=%s failed (non-fatal): %s", job_id, exc)
        return None
