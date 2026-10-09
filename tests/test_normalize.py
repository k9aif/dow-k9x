# SPDX-License-Identifier: Apache-2.0
"""Stage NORMALIZE: text passes through, binary files go to Docling, failures stop the upload."""

import os

import pytest

from k9_dow.retrieval import normalize
from k9_dow.retrieval.normalize import NormalizationError, normalize_upload


def test_markdown_passes_through():
    out = normalize_upload({}, "need.md", b"# Need\n\nDetect sUAS at 5 km.")
    assert out["method"] == "text" and "5 km" in out["markdown"]


def test_empty_text_is_refused():
    with pytest.raises(NormalizationError):
        normalize_upload({}, "need.txt", b"   \n")


def test_unsupported_type_is_refused():
    with pytest.raises(NormalizationError, match="Unsupported"):
        normalize_upload({}, "need.exe", b"MZ")


def test_too_large_is_refused():
    with pytest.raises(NormalizationError, match="25 MB"):
        normalize_upload({}, "big.pdf", b"x" * (normalize.MAX_UPLOAD_BYTES + 1))


class _Parser:
    result = {"status": "ok", "filename": "x.pdf", "markdown": "# Converted", "seconds": 1.2}
    seen = {}

    def __init__(self, config=None, url=None):
        _Parser.seen["url"] = url

    def execute(self, payload):
        _Parser.seen["exists"] = os.path.exists(payload["path"])
        _Parser.seen["bytes"] = open(payload["path"], "rb").read()
        return dict(_Parser.result)


@pytest.fixture
def fake_docling(monkeypatch):
    import k9_aif_abb.k9_agents.retrieval.docling_parser as dp
    monkeypatch.setattr(dp, "DoclingParser", _Parser)
    _Parser.result = {"status": "ok", "filename": "x.pdf", "markdown": "# Converted", "seconds": 1.2}
    return _Parser


def test_pdf_goes_to_docling(fake_docling):
    out = normalize_upload({}, "need.pdf", b"%PDF-1.7 bytes")
    assert out == {"markdown": "# Converted", "method": "docling", "chars": 11, "seconds": 1.2}
    assert fake_docling.seen["exists"] and fake_docling.seen["bytes"] == b"%PDF-1.7 bytes"
    assert fake_docling.seen["url"].endswith("/v1/convert/file")


def test_failed_conversion_stops_the_upload(fake_docling):
    fake_docling.result = {"status": "connection_error", "error": "refused"}
    with pytest.raises(NormalizationError, match="could not be converted"):
        normalize_upload({}, "need.docx", b"PK..")


@pytest.mark.skipif(not os.environ.get("DOCLING_ENDPOINT"), reason="DOCLING_ENDPOINT not set")
def test_live_scanned_pdf():
    """The 2025 SecDef memo is a scanned PDF: text only exists after OCR."""
    from pathlib import Path
    from k9_aif_abb.k9_utils.config_loader import load_yaml
    from k9_dow.config.settings import settings
    config = load_yaml(settings.CONFIG_DIR / "config.yaml")   # DAS governance, as the app runs it
    pdf = Path(__file__).resolve().parents[1] / "data/policy/SecDef_Memo_2025-08-20_requirements.pdf"
    out = normalize_upload(config, pdf.name, pdf.read_bytes())
    assert out["method"] == "docling" and out["chars"] > 5000
    assert "Joint" in out["markdown"]
