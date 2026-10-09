# SPDX-License-Identifier: Apache-2.0
# Shared ICD markdown composition -- used by both the API layer
# (app.py, serving /view and /download on demand) and the orchestrator
# layer (jcids_orchestrator.py, uploading a durable copy to S3), so a
# reviewer sees the identical document either way.

from __future__ import annotations

import json
import os
import re
from datetime import datetime

from k9_dow.utils.dodaf_views import label_view, relabel_views
from typing import Any, Optional


def icd_metadata(filename: str, job_id: str = "", stage: str = "") -> dict:
    """Metadata for the Word ICD: program name from the input file name; job id and stage keep each
    job's (and each stage's) Word file separate in object storage."""
    return {
        "program_name": (filename or "document").rsplit(".", 1)[0].replace("_", " "),
        "date": datetime.now().strftime("%d %B %Y"),
        "version": "1.0",
        "job_id": job_id,
        "stage": stage,
    }


def extract_source_title(source_markdown: str) -> str:
    """Pull the input document's own title from its first Markdown heading
    (e.g. "# CAPABILITY DEVELOPMENT DOCUMENT (CDD) FOR IRONCLAD INCREMENT 1"),
    so the generated ICD is titled after the document it's actually about
    instead of a generic label. Returns "" if no heading is found."""
    if not source_markdown:
        return ""
    for line in source_markdown.splitlines():
        line = line.strip()
        if line.startswith("# "):
            return line[2:].strip()
        if line:
            # First non-blank line wasn't a heading -- this source doesn't
            # lead with one, so don't guess by scanning further into the body.
            break
    return ""


def strip_json_blocks(text: str) -> str:
    """Drop fenced ```json code blocks -- agents restate their prose answer as
    a trailing JSON block, which reads as raw tool output in a human-facing
    document rather than adding new information. Also drops a short
    "Structured Output" heading/label immediately preceding the block, so no
    dangling empty header is left behind."""
    if not text:
        return text
    cleaned = re.sub(
        r"(?:^|\n)\s*(?:#{2,4}\s*Structured[^\n]*|\*\*Structured[^\n]*\*\*:?)\s*\n+```json.*?```",
        "",
        text,
        flags=re.DOTALL | re.IGNORECASE,
    )
    cleaned = re.sub(r"```json.*?```", "", cleaned, flags=re.DOTALL | re.IGNORECASE)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    cleaned = cleaned.strip()
    # If stripping the JSON block(s) ate the *entire* output, the agent had
    # no prose narrative at all -- e.g. ModelExtractorAgent is explicitly
    # prompted to "Output as structured JSON" with nothing else. Falling
    # through to an empty string here silently threw away real extracted
    # data and rendered section 1.1 as "*No output generated.*" even
    # though every downstream agent proves the extraction succeeded.
    # Keep the original (still-fenced) text instead -- it renders as a
    # readable code block rather than vanishing.
    return cleaned if cleaned else text.strip()


def _try_parse_json_only(text: str) -> Optional[Any]:
    """Return the parsed value if `text` is ENTIRELY a JSON object/array
    (optionally wrapped in a single ```json ... ``` fence with nothing
    else around it). Returns None for real prose, prose+trailing-JSON, or
    anything that doesn't parse -- callers fall back to the raw text in
    those cases."""
    t = text.strip()
    m = re.fullmatch(r"```(?:json)?\s*(.*?)\s*```", t, flags=re.DOTALL | re.IGNORECASE)
    if m:
        t = m.group(1).strip()
    if not t or t[0] not in "{[":
        return None
    try:
        return json.loads(t)
    except (json.JSONDecodeError, ValueError):
        return None


def extract_text(obj) -> str:
    """Extract readable text from any agent output structure."""
    if obj is None:
        return ""
    if isinstance(obj, str):
        stripped = obj.strip()
        # An agent prompted to answer in pure JSON with no prose at all
        # (ModelExtractorAgent: "Output as structured JSON") lands here as
        # a raw string. Parse it and re-run it through this same function
        # so the dict/list branches below turn it into readable markdown
        # bullets instead of leaving a raw ```json fence in a human-facing
        # document -- only when it actually produces something, so real
        # prose (which never parses as bare JSON) is untouched.
        parsed = _try_parse_json_only(stripped)
        if parsed is not None:
            formatted = extract_text(parsed)
            if formatted:
                return formatted
        return stripped
    if isinstance(obj, dict):
        # Try "output" key first (standard agent result)
        if "output" in obj:
            result = extract_text(obj["output"])
            if result:
                return result
        # Skip internal keys, collect everything else
        skip = {"agent", "status", "squad_id", "steps", "iterations",
                "evidence", "final_confidence", "disposition",
                "remaining_steps", "notes", "source_markdown",
                "prior_outputs", "filename", "icd_metadata",
                "document_type", "job_id", "correlation_id"}
        parts = []
        for k, v in obj.items():
            if k in skip:
                continue
            if isinstance(v, str) and v.strip():
                parts.append(f"**{k}:** {v}")
            elif isinstance(v, (int, float)):
                parts.append(f"**{k}:** {v}")
            elif isinstance(v, list):
                parts.append(f"**{k}:**")
                for item in v:
                    if isinstance(item, dict):
                        line = ", ".join(f"{ik}: {iv}" for ik, iv in item.items()
                                        if isinstance(iv, (str, int, float)))
                        parts.append(f"- {line}")
                    else:
                        parts.append(f"- {item}")
            elif isinstance(v, dict):
                inner = extract_text(v)
                if inner:
                    parts.append(f"**{k}:**\n{inner}")
        return "\n".join(parts)
    if isinstance(obj, list):
        parts = []
        for i, item in enumerate(obj, 1):
            parts.append(f"{i}. {extract_text(item)}")
        return "\n".join(parts)
    return str(obj)


def nest_section(text: str, level: int = 3, drop_title: bool = True) -> str:
    """An agent's Markdown placed under a DAS section heading of ``level``: its own leading title
    (redundant with the section heading) is dropped and its headings are demoted below ``level``."""
    lines = (text or "").strip().split("\n")
    if drop_title and lines and re.match(r"^#{1,6}\s", lines[0]):
        lines = lines[1:]
        while lines and not lines[0].strip():
            lines = lines[1:]
    levels = [len(m.group(1)) for line in lines if (m := re.match(r"^(#{1,6})\s", line))]
    if levels:
        shift = level + 1 - min(levels)
        lines = [re.sub(r"^(#{1,6})(?=\s)", lambda m: "#" * max(1, min(6, len(m.group(1)) + shift)), line)
                 for line in lines]
    return "\n".join(lines).strip()


def _job_date(job_id: str) -> str:
    m = re.search(r"(\d{4})(\d{2})(\d{2})", job_id or "")
    return f"{m.group(1)}-{m.group(2)}-{m.group(3)}" if m else datetime.now().strftime("%Y-%m-%d")


def with_computed_score(stage_result: dict, gate_id: str, job_id: str = "") -> dict:
    """The stage result with one readiness score throughout: the computed one (gates/readiness.py).
    Jobs stored before the score was computed in code get it computed here from the stored verdicts;
    every later section restating a score is aligned to it; date placeholders are filled."""
    from k9_dow.gates.gate_registry import DAS_GATES
    from k9_dow.gates.readiness import align_score, apply_computed_score

    when = _job_date(job_id or stage_result.get("job_id", ""))
    gate = dict(stage_result.get("gate_readiness") or {})
    rs = gate.get("readiness_score")
    if not isinstance(rs, dict):
        return stage_result
    score = rs.get("score")
    if score is None:
        loaded = gate.get("criteria") if isinstance(gate.get("criteria"), dict) else {}
        criteria = list(loaded.get("criteria")
                        or (DAS_GATES[gate_id].entry_criteria if gate_id in DAS_GATES else []))
        scored = apply_computed_score(extract_text(rs), gate_id, criteria, when)
        score = scored["score"]
        rs = {**rs, "output": scored["output"], "score": score, "verdicts": scored["verdicts"]}
    gate["readiness_score"] = rs

    def aligned(part: dict) -> dict:
        return {k: ({**v, "output": align_score(extract_text(v), score, when)}
                    if isinstance(v, dict) and k != "readiness_score" and extract_text(v) else v)
                for k, v in part.items()}

    out = {**stage_result, "gate_readiness": aligned(gate)}
    if isinstance(stage_result.get("review_package"), dict):
        out["review_package"] = aligned(stage_result["review_package"])
    return out


def compose_icd(job_data: dict) -> str:
    """Compose a single ICD markdown document from all pipeline outputs."""
    result = job_data.get("result", job_data)
    job_id = result.get("job_id", "unknown")
    gate_id = result.get("gate_id", "")
    result = with_computed_score(result, gate_id or "JROC-VALIDATION", job_id)
    date_str = datetime.now().strftime("%d %B %Y")
    document_title = result.get("document_title") or ""

    lines = []
    if document_title:
        lines.append(f"# {document_title}")
        lines.append("")
        lines.append("**Initial Capabilities Document (ICD)**")
    else:
        lines.append("# Initial Capabilities Document (ICD)")
    lines.append("")
    lines.append("## DRAFT — FOR DEMONSTRATION PURPOSES ONLY")
    lines.append("")
    lines.append(f"**Job ID:** {job_id}")
    lines.append(f"**Date:** {date_str}")
    lines.append(f"**Status:** Awaiting HIL Review ({gate_id})")
    lines.append(f"**Classification:** UNCLASSIFIED — PROOF OF CONCEPT")
    model_name = (
        result.get("inference", {}).get("llm_factory", {}).get("models", {}).get("general", {}).get("model", "")
        or os.environ.get("OLLAMA_MODEL", "unknown")
    )
    lines.append(f"**LLM Model:** {model_name}")
    data_sources_label = os.environ.get("KNOWLEDGE_CORPUS_LABEL", "None")
    lines.append(f"**Data Sources:** {data_sources_label}")
    lines.append("")
    lines.append("---")
    lines.append("")

    sections = [
        ("view_generation", "1. Architecture Views", {
            "model_elements": "1.1 Model Elements (Capabilities, Requirements, Systems)",
            "generated_views": "1.2 OV-1 High-Level Operational Concept Graphic",
            "consistency_report": "1.3 Cross-View Consistency Report",
        }),
        ("gate_readiness", "2. Gate Readiness Assessment", {
            "criteria": "2.1 Gate Entry Criteria",
            "evidence": "2.2 Evidence Summary",
            "readiness_score": "2.3 Readiness Score",
            "gap_report": "2.4 Gap Analysis",
        }),
        ("review_package", "3. Review Package", {
            "artifact_manifest": "3.1 Artifact Manifest",
            "completeness_check": "3.2 Completeness Assessment",
            "review_package": "3.3 Package Summary",
        }),
    ]

    for section_key, section_title, subsections in sections:
        section = result.get(section_key, {})
        if not section:
            continue
        lines.append(f"## {section_title}")
        lines.append("")

        for agent_key, subsection_title in subsections.items():
            agent_output = section.get(agent_key, {})
            if not isinstance(agent_output, dict):
                if isinstance(agent_output, str) and agent_output.strip():
                    lines.append(f"### {subsection_title}")
                    lines.append("")
                    lines.append(nest_section(strip_json_blocks(agent_output.strip()),
                                              drop_title=agent_key != "generated_views"))
                    lines.append("")
                continue
            output_text = strip_json_blocks(extract_text(agent_output)) or "*No output generated.*"
            if agent_key == "generated_views":
                vt = re.search(r"View(?:\s+ID)?:\**\s*((?:AV|CV|OV|SV|SvcV|TV|DIV|PV|StdV)-\d+[a-z]?)", output_text)
                output_text = label_view(output_text, vt.group(1) if vt else "OV-1")
            lines.append(f"### {subsection_title}")
            lines.append("")
            lines.append(nest_section(str(output_text), drop_title=agent_key != "generated_views"))
            lines.append("")

    lines.append("---")
    lines.append("")
    lines.append(f"*Generated by DAS (Defense Acquisition System) — Built on K9-AIF Framework*")
    lines.append(f"*{date_str} | {job_id}*")

    return relabel_views("\n".join(lines))
