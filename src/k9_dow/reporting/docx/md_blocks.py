from __future__ import annotations

import re
from io import BytesIO

from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

from k9_dow.reporting.models import DiagramSpec


_BULLET = re.compile(r"^(\s*)[-*+]\s+(.*)$")
_NUMBERED = re.compile(r"^(\s*)(\d+)[.)]\s+(.*)$")
_RULE = re.compile(r"^\s*(?:-{3,}|\*{3,}|_{3,})\s*$")
_INLINE = re.compile(r"(\*\*.+?\*\*|__.+?__|`[^`]+`|<br\s*/?>|(?<![\w*])\*(?!\s)[^*]+?\*(?![\w*]))", re.I)


def render_markdown_to_docx(doc: Document, md: str, diagrams: dict[str, bytes] | None = None) -> None:
    diagrams = diagrams or {}
    lines = md.split("\n")
    i = 0
    table_buffer = []
    in_table = False

    while i < len(lines):
        line = lines[i]

        if line.lstrip().startswith("|") and "|" in line.lstrip()[1:]:
            table_buffer.append(line.strip())
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

        heading = re.match(r"^(#{1,6})\s+(.*)$", line)
        bullet = _BULLET.match(line)
        numbered = _NUMBERED.match(line)
        if heading:
            doc.add_heading(_plain(heading.group(2)), level=min(len(heading.group(1)), 4))
        elif _RULE.match(line):
            pass
        elif line.startswith("> "):
            p = doc.add_paragraph(style="Intense Quote")
            _add_formatted_runs(p, line[2:].strip())
        elif bullet:
            indent = len(bullet.group(1).expandtabs(4))
            level = 0 if indent < 2 else 1 if indent < 6 else 2       # 2- or 4-space nesting
            p = doc.add_paragraph(style="List Bullet" if level == 0 else f"List Bullet {level + 1}")
            _add_formatted_runs(p, bullet.group(2).strip())
        elif numbered:
            # The source's own number, with a hanging indent. Word's "List Number" style keeps
            # counting across the whole document (5…, 10–13, 14–17 in the Milestone package).
            indent = len(numbered.group(1).expandtabs(4)) // 2
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Inches(0.3 + 0.25 * indent)
            p.paragraph_format.first_line_indent = Inches(-0.3)
            p.add_run(f"{numbered.group(2)}.\t")
            _add_formatted_runs(p, numbered.group(3).strip())
        elif line.startswith("![") and "](" in line:
            _add_diagram_placeholder(doc, line)
        else:
            p = doc.add_paragraph()
            _add_formatted_runs(p, line.strip())

        i += 1

    if in_table:
        _flush_table(doc, table_buffer)


def _plain(text: str) -> str:
    """Text without Markdown emphasis or code marks (headings)."""
    return re.sub(r"\*\*|__|`", "", text).strip()


def _add_formatted_runs(paragraph, text: str, bold: bool = False) -> None:
    """Bold, italic, code and <br> line breaks as Word runs, not literal Markdown."""
    for part in _INLINE.split(text):
        if not part:
            continue
        if re.fullmatch(r"<br\s*/?>", part, re.I):
            paragraph.add_run().add_break()
        elif (part.startswith("**") and part.endswith("**")) or (part.startswith("__") and part.endswith("__")):
            _add_formatted_runs(paragraph, part[2:-2], bold=True)
        elif part.startswith("`") and part.endswith("`"):
            run = paragraph.add_run(part[1:-1])
            run.bold = bold
            run.font.name = "Consolas"
        elif part.startswith("*") and part.endswith("*") and len(part) > 2:
            run = paragraph.add_run(part[1:-1])
            run.italic = True
            run.bold = bold
        else:
            run = paragraph.add_run(part)
            run.bold = bold


def _flush_table(doc: Document, rows: list[str]) -> None:
    parsed = []
    for row in rows:
        cells = [c.strip() for c in row.strip().strip("|").split("|")]
        if all(re.match(r"^:?-+:?$", c) for c in cells if c):
            continue
        parsed.append(cells)

    if not parsed:
        return

    ncols = max(len(r) for r in parsed)
    table = doc.add_table(rows=len(parsed), cols=ncols)
    table.style = "Table Grid"

    for ri, row_data in enumerate(parsed):
        for ci, cell_text in enumerate(row_data[:ncols]):
            paragraph = table.cell(ri, ci).paragraphs[0]
            _add_formatted_runs(paragraph, cell_text, bold=(ri == 0))


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
