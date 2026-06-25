# SPDX-License-Identifier: Apache-2.0
# DoW Architecture Workbench — RoutingClassifierAgent (SBB)

import json
import logging
from typing import Any, Dict, Optional

from k9_aif_abb.k9_core.agent.base_agent import BaseAgent
from k9_aif_abb.k9_inference.models.inference_request import InferenceRequest
from k9_aif_abb.k9_utils.llm_invoke import llm_invoke

log = logging.getLogger(__name__)


class RoutingClassifierAgent(BaseAgent):
    """
    LLM-based document classifier used when deterministic routing rules
    are inconclusive.

    Classifies documents into BD, DODAF, JCIDS, SE, or UNKNOWN.
    """

    layer = "DoW RoutingClassifier SBB"

    def __init__(self, config: Optional[Dict[str, Any]] = None, monitor=None, **kwargs):
        super().__init__(config or {}, monitor=monitor, **kwargs)

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        source = payload.get("source_markdown") or ""
        text_preview = source[:3000]

        if not text_preview.strip():
            self.publish_event({"type": "AgentCompleted", "agent": "RoutingClassifierAgent"})
            return {
                "agent": "RoutingClassifierAgent",
                "output": "Empty document — classified as UNKNOWN.",
                "classification": "UNKNOWN",
                "document_type": "unknown",
                "confidence": 0.0,
                "rationale": "Empty document",
            }

        prompt = (
            f"Role: {self.config.get('role', 'Document Classification Specialist')}\n"
            f"Goal: {self.config.get('goal', 'Classify documents into architecture pipeline categories')}\n\n"
            "## Task\n"
            "Classify this document into exactly one category:\n"
            "- BD: business development, call reports, meeting notes, engagement\n"
            "- DODAF: architecture, mission, capability, operational, system, DoDAF\n"
            "- JCIDS: requirements, ICD, CDD, KPP, capability gap, JCIDS\n"
            "- SE: systems engineering, functional analysis, verification, specification\n"
            "- UNKNOWN: does not fit any category\n\n"
            "Return JSON only:\n"
            '{"classification": "...", "document_type": "...", "confidence": 0.0-1.0, '
            '"rationale": "...", "dodaf_eligible": true/false, "jcids_eligible": true/false, '
            '"se_eligible": true/false}\n\n'
            f"## Source Document\n{text_preview}\n"
        )

        try:
            req = InferenceRequest(
                prompt=prompt,
                task_type=self.config.get("model", "reasoning"),
                metadata={"agent": "RoutingClassifierAgent"},
            )
            resp = llm_invoke(self.config, req)
            raw = resp.output.strip()

            json_start = raw.find("{")
            json_end = raw.rfind("}") + 1
            if json_start >= 0 and json_end > json_start:
                data = json.loads(raw[json_start:json_end])
            else:
                data = {
                    "classification": "UNKNOWN",
                    "document_type": "unknown",
                    "confidence": 0.3,
                    "rationale": "LLM did not return valid JSON",
                }
        except Exception as exc:
            log.warning("[RoutingClassifier] LLM classification failed: %s", exc)
            data = {
                "classification": "UNKNOWN",
                "document_type": "unknown",
                "confidence": 0.0,
                "rationale": f"Classification failed: {exc}",
            }

        self.publish_event({"type": "AgentCompleted", "agent": "RoutingClassifierAgent"})
        return {
            "agent": "RoutingClassifierAgent",
            "output": f"Classification: {data.get('classification', 'UNKNOWN')} "
                      f"(confidence: {data.get('confidence', 0.0)})",
            **data,
        }
