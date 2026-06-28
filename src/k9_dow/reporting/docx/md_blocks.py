from __future__ import annotations

import re
from io import BytesIO

from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

from k9_dow.reporting.models import DiagramSpec


def render_markdown_to_docx(doc: Document, md: str, diagrams: dict[str, bytes] | None = None) -> None:
    diagrams = diagrams or {}
    lines = md.split("\n")
    i = 0
    table_buffer = []
    in_table = False

    while i < len(lines):
        line = lines[i]

        if line.startswith("|") and "|" in line[1:]:
            table_buffer.append(line)
            in_table = True
            i += 1
            continue
        elif in_table:
            _flush_table(doc, table_buffer)
            table_buffer = []
            in_table = False

        if not line.strip():
            i += 1
            continue

        if line.startswith("# "):
            doc.add_heading(line[2:].strip(), level=1)
        elif line.startswith("## "):
            doc.add_heading(line[3:].strip(), level=2)
        elif line.startswith("### "):
            doc.add_heading(line[4:].strip(), level=3)
        elif line.startswith("#### "):
            doc.add_heading(line[5:].strip(), level=4)
        elif line.startswith("> "):
            p = doc.add_paragraph(style="Intense Quote")
            _add_formatted_runs(p, line[2:].strip())
        elif line.startswith("- ") or line.startswith("* "):
            p = doc.add_paragraph(style="List Bullet")
            _add_formatted_runs(p, line[2:].strip())
        elif re.match(r"^\d+\.\s", line):
            p = doc.add_paragraph(style="List Number")
            _add_formatted_runs(p, re.sub(r"^\d+\.\s", "", line).strip())
        elif line.startswith("---"):
            pass
        elif line.startswith("![") and "](" in line:
            _add_diagram_placeholder(doc, line)
        else:
            p = doc.add_paragraph()
            _add_formatted_runs(p, line.strip())

        i += 1

    if in_table:
        _flush_table(doc, table_buffer)


def _add_formatted_runs(paragraph, text: str) -> None:
    parts = re.split(r"(\*\*.*?\*\*)", text)
    for part in parts:
        if part.startswith("**") and part.endswith("**"):
            run = paragraph.add_run(part[2:-2])
            run.bold = True
        else:
            paragraph.add_run(part)


def _flush_table(doc: Document, rows: list[str]) -> None:
    parsed = []
    for row in rows:
        cells = [c.strip() for c in row.strip().strip("|").split("|")]
        if all(re.match(r"^[-:]+$", c) for c in cells):
            continue
        parsed.append(cells)

    if not parsed:
        return

    ncols = max(len(r) for r in parsed)
    table = doc.add_table(rows=len(parsed), cols=ncols)
    table.style = "Table Grid"

    for ri, row_data in enumerate(parsed):
        for ci, cell_text in enumerate(row_data):
            if ci < ncols:
                cell = table.cell(ri, ci)
                cell.text = cell_text
                if ri == 0:
                    for p in cell.paragraphs:
                        for run in p.runs:
                            run.bold = True


def _add_diagram_placeholder(doc: Document, line: str) -> None:
    match = re.match(r"!\[(.*?)\]\((.*?)\)", line)
    if match:
        caption = match.group(1)
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(f"[Diagram: {caption}]")
        run.italic = True
        run.font.size = Pt(10)


def add_diagram_image(doc: Document, png_bytes: bytes, caption: str, width: float = 6.0) -> None:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run()
    run.add_picture(BytesIO(png_bytes), width=Inches(width))

    cap = doc.add_paragraph()
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = cap.add_run(caption)
    run.bold = True
    run.font.size = Pt(10)
