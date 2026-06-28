from __future__ import annotations

import logging
import re
from typing import Any

from k9_dow.reporting.models import IcdContent, IcdMetadata, IcdSection, DiagramSpec
from k9_dow.reporting.template_engine import TemplateEngine
from k9_dow.reporting.section_mapper import SectionMapper
from k9_dow.reporting.docx.docx_renderer import DocxRenderer
from k9_dow.reporting.diagrams.plantuml_renderer import PlantUmlRenderer

log = logging.getLogger(__name__)


class IcdReportBuilder:

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        self._config = config or {}
        self._template_engine = TemplateEngine()
        self._section_mapper = SectionMapper()
        self._docx_renderer = DocxRenderer()
        self._puml_renderer = PlantUmlRenderer()

    def build(self, prior_outputs: dict[str, Any], metadata: dict[str, Any]) -> bytes:
        tokens = self._section_mapper.to_tokens(prior_outputs, metadata)
        resolved_md = self._template_engine.resolve(tokens)
        diagram_specs = self._section_mapper.extract_diagrams(prior_outputs)

        for spec in diagram_specs:
            if spec.kind == "ov1" and spec.source:
                from k9_dow.reporting.diagrams.graph_view_builder import build_traceability_puml
                puml = build_traceability_puml({"capabilities": [], "requirements": [], "links": []})
                spec.png_bytes = self._puml_renderer.render_png(puml)

        content = self._parse_resolved_markdown(resolved_md, metadata, diagram_specs)

        return self._docx_renderer.render(content)

    def build_and_store(
        self,
        prior_outputs: dict[str, Any],
        metadata: dict[str, Any],
        config: dict[str, Any] | None = None,
    ) -> str:
        docx_bytes = self.build(prior_outputs, metadata)
        cfg = config or self._config

        try:
            from k9_aif_abb.k9_factories.object_storage_factory import ObjectStorageFactory
            store = ObjectStorageFactory.create(cfg)
            program = metadata.get("program_name", "unknown").replace(" ", "_").lower()
            key = f"icd/{program}/ICD_{program}.docx"
            uri = store.upload("dow-reports", key, docx_bytes, {"type": "ICD", "program": program})
            log.info("[IcdReportBuilder] Stored ICD at %s", uri)
            return uri
        except Exception as exc:
            log.warning("[IcdReportBuilder] Object storage unavailable: %s — saving locally", exc)
            from k9_dow.config.settings import settings
            output_dir = settings.OUTPUT_DIR
            output_dir.mkdir(parents=True, exist_ok=True)
            program = metadata.get("program_name", "unknown").replace(" ", "_").lower()
            path = output_dir / f"ICD_{program}.docx"
            path.write_bytes(docx_bytes)
            log.info("[IcdReportBuilder] Saved ICD to %s", path)
            return str(path)

    def _parse_resolved_markdown(
        self,
        md: str,
        metadata: dict[str, Any],
        diagrams: list[DiagramSpec],
    ) -> IcdContent:
        meta = IcdMetadata(
            program_name=metadata.get("program_name", ""),
            acat_level=metadata.get("acat_level", ""),
            validation_authority=metadata.get("validation_authority", ""),
            approval_authority=metadata.get("approval_authority", ""),
            milestone_authority=metadata.get("milestone_authority", ""),
            designation=metadata.get("designation", ""),
            prepared_for=metadata.get("prepared_for", ""),
            date=metadata.get("date", ""),
            version=metadata.get("version", "1.0"),
        )

        sections = []
        exec_summary = ""
        current_section = None
        current_body_lines = []

        for line in md.split("\n"):
            heading_match = re.match(r"^(#{1,4})\s+(.+)$", line)
            if heading_match:
                if current_section:
                    current_section.body = "\n".join(current_body_lines)
                    sections.append(current_section)
                    current_body_lines = []

                level = len(heading_match.group(1))
                title = heading_match.group(2).strip()

                if "EXECUTIVE SUMMARY" in title.upper():
                    current_section = None
                    continue

                current_section = IcdSection(id=title, level=level, title=title)
            elif current_section:
                current_body_lines.append(line)
            elif "EXECUTIVE SUMMARY" in md[:md.find("\n##")] if "\n##" in md else "":
                exec_summary += line + "\n"

        if current_section:
            current_section.body = "\n".join(current_body_lines)
            sections.append(current_section)

        if diagrams and sections:
            for spec in diagrams:
                if spec.kind == "ov1":
                    for s in sections:
                        if "Appendix A" in s.title or "OV-1" in s.title:
                            s.diagrams.append(spec)
                            break

        return IcdContent(
            metadata=meta,
            executive_summary=exec_summary,
            sections=sections,
        )
