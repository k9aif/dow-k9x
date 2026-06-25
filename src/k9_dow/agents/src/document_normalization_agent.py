# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, Optional

from k9_dow.agents.src.base_dow_agent import BaseDowAgent
from k9_dow.contracts.artifacts import DowAgentResult
from k9_dow.contracts.payloads import DowAgentPayload

log = logging.getLogger(__name__)


class DocumentNormalizationAgent(BaseDowAgent):
    """
    Pure extraction agent — no LLM invocation.

    Converts uploaded documents (MD, TXT, PDF, DOCX, XLSX, CSV) into
    normalized Markdown text with metadata.
    """

    layer = "DoW DocumentNormalization SBB"
    agent_name = "DocumentNormalizationAgent"

    def run_agent(self, payload: DowAgentPayload) -> DowAgentResult:
        warnings: list[str] = []
        markdown = ""
        metadata: Dict[str, Any] = {}

        if payload.source_markdown:
            markdown = payload.source_markdown
            metadata["conversion_method"] = "passthrough"
        elif payload.metadata.get("raw_path"):
            raw_path = Path(payload.metadata["raw_path"])
            markdown, meta_warnings = self._extract_from_file(raw_path)
            warnings.extend(meta_warnings)
            metadata["conversion_method"] = f"file_extraction:{raw_path.suffix}"
            metadata["file_size"] = raw_path.stat().st_size if raw_path.exists() else 0
        else:
            return DowAgentResult(
                job_id=payload.job_id,
                agent_name=self.agent_name,
                stage_id=payload.stage_id,
                status="failed",
                errors=["No source_markdown or raw_path provided"],
            )

        if not markdown or not markdown.strip():
            return DowAgentResult(
                job_id=payload.job_id,
                agent_name=self.agent_name,
                stage_id=payload.stage_id,
                status="failed",
                errors=["Document produced empty text after normalization"],
                warnings=warnings,
            )

        metadata["char_count"] = len(markdown)
        metadata["line_count"] = markdown.count("\n") + 1

        return DowAgentResult(
            job_id=payload.job_id,
            agent_name=self.agent_name,
            stage_id=payload.stage_id,
            status="completed",
            markdown=markdown,
            json_data=metadata,
            warnings=warnings,
        )

    # ── File extraction dispatch ─────────────────────────────────────────

    def _extract_from_file(self, path: Path) -> tuple[str, list[str]]:
        warnings: list[str] = []
        suffix = path.suffix.lower()

        if not path.exists():
            return "", [f"File not found: {path}"]

        if suffix in (".md", ".markdown", ".txt"):
            return path.read_text(encoding="utf-8", errors="ignore"), warnings

        if suffix == ".docx":
            return self._extract_docx(path, warnings)

        if suffix == ".pdf":
            return self._extract_pdf(path, warnings)

        if suffix in (".csv", ".xlsx"):
            return self._extract_tabular(path, suffix, warnings)

        warnings.append(f"Unsupported file type: {suffix}, attempting raw text decode")
        try:
            return path.read_text(encoding="utf-8", errors="ignore"), warnings
        except Exception as exc:
            return "", warnings + [f"Raw decode failed: {exc}"]

    # ── Format-specific extractors ───────────────────────────────────────

    def _extract_docx(self, path: Path, warnings: list[str]) -> tuple[str, list[str]]:
        try:
            from docx import Document

            doc = Document(str(path))
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            return "\n\n".join(paragraphs), warnings
        except ImportError:
            warnings.append("python-docx not installed; pip install python-docx")
            return "", warnings
        except Exception as exc:
            warnings.append(f"DOCX extraction failed: {exc}")
            return "", warnings

    def _extract_pdf(self, path: Path, warnings: list[str]) -> tuple[str, list[str]]:
        try:
            from pypdf import PdfReader

            reader = PdfReader(str(path))
            pages = []
            for i, page in enumerate(reader.pages):
                text = page.extract_text() or ""
                if text.strip():
                    pages.append(f"<!-- Page {i+1} -->\n{text}")
            if not pages:
                warnings.append("PDF produced no extractable text; may need OCR")
            return "\n\n".join(pages), warnings
        except ImportError:
            warnings.append("pypdf not installed; pip install pypdf")
            return "", warnings
        except Exception as exc:
            warnings.append(f"PDF extraction failed: {exc}")
            return "", warnings

    def _extract_tabular(
        self, path: Path, suffix: str, warnings: list[str]
    ) -> tuple[str, list[str]]:
        try:
            if suffix == ".csv":
                import csv

                with open(path, encoding="utf-8", errors="ignore") as f:
                    reader = csv.reader(f)
                    rows = list(reader)
            else:
                try:
                    from openpyxl import load_workbook

                    wb = load_workbook(str(path), read_only=True, data_only=True)
                    ws = wb.active
                    rows = [[str(c.value or "") for c in row] for row in ws.iter_rows()]
                    wb.close()
                except ImportError:
                    warnings.append("openpyxl not installed; pip install openpyxl")
                    return "", warnings

            if not rows:
                return "", warnings + ["Empty spreadsheet"]

            header = "| " + " | ".join(rows[0]) + " |"
            sep = "| " + " | ".join("---" for _ in rows[0]) + " |"
            body = "\n".join("| " + " | ".join(row) + " |" for row in rows[1:])
            return f"{header}\n{sep}\n{body}", warnings

        except Exception as exc:
            warnings.append(f"Tabular extraction failed: {exc}")
            return "", warnings
