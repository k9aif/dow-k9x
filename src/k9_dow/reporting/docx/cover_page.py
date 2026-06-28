from __future__ import annotations

from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

from k9_dow.reporting.models import IcdMetadata


def add_cover_page(doc: Document, meta: IcdMetadata) -> None:
    for _ in range(3):
        doc.add_paragraph()

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("Initial Capabilities Document (ICD)")
    run.bold = True
    run.font.size = Pt(18)
    run.font.name = "Times New Roman"

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("for")
    run.font.size = Pt(14)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(meta.program_name)
    run.bold = True
    run.font.size = Pt(16)
    run.font.name = "Times New Roman"

    for _ in range(6):
        doc.add_paragraph()

    _add_metadata_table(doc, meta)

    from k9_dow.reporting.docx.styles import add_page_break
    add_page_break(doc)


def _add_metadata_table(doc: Document, meta: IcdMetadata) -> None:
    rows = [
        ("Potential ACAT", meta.acat_level),
        ("Validation Authority", meta.validation_authority),
        ("Approval Authority", meta.approval_authority),
        ("Milestone Decision Authority", meta.milestone_authority),
        ("Designation", meta.designation),
        ("Prepared for", meta.prepared_for),
        ("Date", meta.date),
    ]
    rows = [(k, v) for k, v in rows if v]

    for label, value in rows:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(f"{label}: {value}")
        run.bold = True
        run.font.size = Pt(11)
        run.font.name = "Times New Roman"
