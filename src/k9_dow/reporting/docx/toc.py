from __future__ import annotations

from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement


def add_toc(doc: Document) -> None:
    _add_field_heading(doc, "TABLE OF CONTENTS")
    _add_field(doc, r'TOC \o "1-3" \h \z \u')
    from k9_dow.reporting.docx.styles import add_page_break
    add_page_break(doc)


def add_table_of_figures(doc: Document) -> None:
    _add_field_heading(doc, "Table of Figures")
    _add_field(doc, r'TOC \h \z \c "Figure"')


def add_table_of_tables(doc: Document) -> None:
    _add_field_heading(doc, "Table of Tables")
    _add_field(doc, r'TOC \h \z \c "Table"')


def _add_field_heading(doc: Document, title: str) -> None:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(title)
    run.bold = True
    run.font.size = Pt(14)
    run.font.name = "Times New Roman"


def _add_field(doc: Document, instr: str) -> None:
    p = doc.add_paragraph()
    run = p.add_run()
    r_element = run._r

    fld_begin = OxmlElement("w:fldChar")
    fld_begin.set(qn("w:fldCharType"), "begin")
    r_element.append(fld_begin)

    instr_el = OxmlElement("w:instrText")
    instr_el.set(qn("xml:space"), "preserve")
    instr_el.text = f" {instr} "
    r_element.append(instr_el)

    fld_sep = OxmlElement("w:fldChar")
    fld_sep.set(qn("w:fldCharType"), "separate")
    r_element.append(fld_sep)

    fld_end = OxmlElement("w:fldChar")
    fld_end.set(qn("w:fldCharType"), "end")
    r_element.append(fld_end)
