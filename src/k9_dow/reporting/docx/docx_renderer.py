from __future__ import annotations

import io
import logging

from k9_dow.reporting.models import IcdContent
from k9_dow.reporting.docx.styles import (
    create_document, apply_classification_headers, apply_line_numbering, add_page_break,
)
from k9_dow.reporting.docx.cover_page import add_cover_page
from k9_dow.reporting.docx.toc import add_toc, add_table_of_figures, add_table_of_tables
from k9_dow.reporting.docx.md_blocks import render_markdown_to_docx, add_diagram_image

log = logging.getLogger(__name__)


class DocxRenderer:

    def render(self, content: IcdContent) -> bytes:
        doc = create_document()

        add_cover_page(doc, content.metadata)

        add_toc(doc)
        add_table_of_figures(doc)
        add_table_of_tables(doc)
        add_page_break(doc)

        if content.executive_summary:
            doc.add_heading("EXECUTIVE SUMMARY", level=1)
            render_markdown_to_docx(doc, content.executive_summary)
            add_page_break(doc)

        for section in content.sections:
            doc.add_heading(section.title, level=section.level)
            if section.body:
                render_markdown_to_docx(doc, section.body)

            for diagram in section.diagrams:
                if diagram.png_bytes:
                    add_diagram_image(doc, diagram.png_bytes, diagram.caption)
                else:
                    from docx.shared import Pt
                    from docx.enum.text import WD_ALIGN_PARAGRAPH
                    p = doc.add_paragraph()
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    run = p.add_run(f"[Diagram: {diagram.caption} — NOT GENERATED]")
                    run.italic = True
                    run.font.size = Pt(10)

        if content.acronyms:
            doc.add_heading("Appendix C — Acronym List", level=1)
            _render_acronym_table(doc, content.acronyms)

        if content.references:
            doc.add_heading("Appendix B — References", level=1)
            for ref in content.references:
                doc.add_paragraph(ref, style="List Bullet")

        if content.glossary:
            doc.add_heading("Appendix K — Glossary", level=1)
            _render_glossary(doc, content.glossary)

        apply_classification_headers(doc, content.metadata.classification)
        apply_line_numbering(doc)

        buf = io.BytesIO()
        doc.save(buf)
        buf.seek(0)
        log.info("[DocxRenderer] ICD document rendered: %d sections", len(content.sections))
        return buf.read()


def _render_acronym_table(doc, acronyms: dict[str, str]) -> None:
    table = doc.add_table(rows=1 + len(acronyms), cols=2)
    table.style = "Table Grid"
    table.cell(0, 0).text = "Acronym"
    table.cell(0, 1).text = "Definition"
    for r in table.cell(0, 0).paragraphs[0].runs:
        r.bold = True
    for r in table.cell(0, 1).paragraphs[0].runs:
        r.bold = True
    for i, (acr, defn) in enumerate(sorted(acronyms.items()), start=1):
        table.cell(i, 0).text = acr
        table.cell(i, 1).text = defn


def _render_glossary(doc, glossary: dict[str, str]) -> None:
    for term, definition in sorted(glossary.items()):
        p = doc.add_paragraph()
        run = p.add_run(f"{term}: ")
        run.bold = True
        p.add_run(definition)
