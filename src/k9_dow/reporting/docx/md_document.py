# SPDX-License-Identifier: Apache-2.0
# K9-AIF Framework
"""A Word (.docx) version of a markdown document (the ICD or the Milestone
review package), built from the same markdown the UI shows, so the two never
differ. Uses DAS's existing page setup, classification banners and markdown
block renderer."""

from __future__ import annotations

import io
import re

from k9_dow.reporting.docx.md_blocks import render_markdown_to_docx
from k9_dow.reporting.docx.styles import apply_classification_headers, create_document


def _clean(md: str) -> str:
    # HTML comments and code fences are not document content
    md = re.sub(r"<!--.*?-->", "", md, flags=re.S)
    md = re.sub(r"^```.*$", "", md, flags=re.M)
    return md


def markdown_to_docx(md: str, classification: str = "UNCLASSIFIED — PROOF OF CONCEPT") -> bytes:
    doc = create_document()
    apply_classification_headers(doc, classification)
    render_markdown_to_docx(doc, _clean(md))
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()
