from __future__ import annotations

from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement


def create_document() -> Document:
    doc = Document()
    _apply_page_setup(doc)
    _apply_default_styles(doc)
    return doc


def _apply_page_setup(doc: Document) -> None:
    for section in doc.sections:
        section.left_margin = Inches(1.25)
        section.right_margin = Inches(1.0)
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)


def _apply_default_styles(doc: Document) -> None:
    style = doc.styles["Normal"]
    style.font.name = "Times New Roman"
    style.font.size = Pt(11)
    style.paragraph_format.space_after = Pt(6)


def apply_classification_headers(doc: Document, classification: str = "UNCLASSIFIED") -> None:
    for section in doc.sections:
        _mark_header_footer(section.header, classification)
        _mark_header_footer(section.footer, classification)


def _mark_header_footer(container, text: str) -> None:
    if container.paragraphs:
        p = container.paragraphs[0]
        p.clear()
    else:
        p = container.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(text)
    run.bold = True
    run.font.size = Pt(14)
    run.font.name = "Times New Roman"


def apply_line_numbering(doc: Document) -> None:
    for section in doc.sections:
        sect_pr = section._sectPr
        ln = OxmlElement("w:lnNumType")
        ln.set(qn("w:countBy"), "1")
        ln.set(qn("w:start"), "1")
        ln.set(qn("w:restart"), "continuous")
        ln.set(qn("w:distance"), "360")
        sect_pr.append(ln)


def add_page_break(doc: Document) -> None:
    from docx.enum.text import WD_BREAK
    p = doc.add_paragraph()
    p.add_run().add_break(WD_BREAK.PAGE)
