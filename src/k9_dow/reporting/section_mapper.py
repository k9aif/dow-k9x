from __future__ import annotations

import logging
from typing import Any

from k9_dow.reporting.models import DiagramSpec

log = logging.getLogger(__name__)

_AGENT_TO_TOKEN_MAP = {
    "model_elements": [
        "CAPABILITIES_TABLE", "TASKS_DESCRIPTION", "TASK_ATTRIBUTES",
    ],
    "generated_views": [
        "OV1_CONTENT", "PROCESS_VIEW",
    ],
    "consistency_report": [],
    "criteria": [],
    "evidence": [],
    "readiness_score": [
        "GAP_SCORING", "GAP_PRIORITIZATION",
    ],
    "gap_report": [
        "CAPABILITY_GAPS_DETAIL", "CAPABILITY_GAP_TABLE", "GAPS_OVERVIEW",
    ],
    "coverage_report": [],
    "proposed_links": [],
    "validated_links": [],
    "orphans": [],
    "baseline_drift": [],
    "funding_drift": [],
    "drift_alerts": [],
    "artifact_manifest": [],
    "completeness_check": [],
    "review_package": [
        "EXECUTIVE_SUMMARY", "SOLUTION_APPROACH_SUMMARY", "FINAL_RECOMMENDATIONS",
    ],
}


class SectionMapper:

    def to_tokens(self, prior_outputs: dict[str, Any], metadata: dict[str, Any]) -> dict[str, str]:
        tokens: dict[str, str] = {}

        tokens["PROGRAM_NAME"] = metadata.get("program_name", "")
        tokens["ACAT_LEVEL"] = metadata.get("acat_level", "")
        tokens["VALIDATION_AUTHORITY"] = metadata.get("validation_authority", "")
        tokens["APPROVAL_AUTHORITY"] = metadata.get("approval_authority", "")
        tokens["MILESTONE_AUTHORITY"] = metadata.get("milestone_authority", "")
        tokens["DESIGNATION"] = metadata.get("designation", "")
        tokens["PREPARED_FOR"] = metadata.get("prepared_for", "")
        tokens["DATE"] = metadata.get("date", "")
        tokens["VERSION"] = metadata.get("version", "1.0")
        tokens["PROGRAM_SCOPE"] = metadata.get("program_scope", metadata.get("program_name", ""))

        for result_key, output in prior_outputs.items():
            output_text = self._extract_text(output)
            if not output_text:
                continue

            token_keys = _AGENT_TO_TOKEN_MAP.get(result_key, [])
            if token_keys:
                for tk in token_keys:
                    if tk not in tokens or not tokens[tk]:
                        tokens[tk] = output_text
            else:
                tokens[result_key.upper()] = output_text

        return tokens

    def extract_diagrams(self, prior_outputs: dict[str, Any]) -> list[DiagramSpec]:
        diagrams = []

        views = prior_outputs.get("generated_views", {})
        if isinstance(views, dict):
            view_output = views.get("output", "")
        elif isinstance(views, str):
            view_output = views
        else:
            view_output = ""

        if view_output and "OV-1" in str(views):
            diagrams.append(DiagramSpec(
                kind="ov1",
                source=view_output[:2000],
                caption="Operational Context and Overview Diagram (OV-1)",
            ))

        return diagrams

    @staticmethod
    def _extract_text(output: Any) -> str:
        if isinstance(output, str):
            return output.strip()
        if isinstance(output, dict):
            for key in ("output", "content", "text", "body"):
                if key in output and isinstance(output[key], str):
                    return output[key].strip()
        return ""
