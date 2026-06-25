# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import json
import logging
from typing import Any, Dict, Optional

from k9_dow.agents.src.base_dow_agent import BaseDowAgent
from k9_dow.contracts.artifacts import DowAgentResult
from k9_dow.contracts.payloads import DowAgentPayload
from k9_dow.utils.markdown_utils import extract_first_json

log = logging.getLogger(__name__)


class RoutingClassifierAgent(BaseDowAgent):
    """
    LLM-based document classifier used when deterministic routing rules
    are inconclusive.

    Classifies documents into BD, DODAF, JCIDS, SE, or UNKNOWN.
    """

    layer = "DoW RoutingClassifier SBB"
    agent_name = "RoutingClassifierAgent"

    def run_agent(self, payload: DowAgentPayload) -> DowAgentResult:
        text_preview = payload.source_markdown[:3000] if payload.source_markdown else ""

        if not text_preview.strip():
            return DowAgentResult(
                job_id=payload.job_id,
                agent_name=self.agent_name,
                stage_id=payload.stage_id,
                status="completed",
                json_data={
                    "classification": "UNKNOWN",
                    "document_type": "unknown",
                    "confidence": 0.0,
                    "rationale": "Empty document",
                },
            )

        prompt = self.build_prompt(
            role="Document Classification Specialist",
            task=(
                "Classify this document into exactly one category:\n"
                "- BD: business development, call reports, meeting notes, engagement\n"
                "- DODAF: architecture, mission, capability, operational, system, DoDAF\n"
                "- JCIDS: requirements, ICD, CDD, KPP, capability gap, JCIDS\n"
                "- SE: systems engineering, functional analysis, verification, specification\n"
                "- UNKNOWN: does not fit any category\n\n"
                "Return JSON only:\n"
                '{"classification": "...", "document_type": "...", "confidence": 0.0-1.0, '
                '"rationale": "...", "dodaf_eligible": true/false, "jcids_eligible": true/false, '
                '"se_eligible": true/false}'
            ),
            source_text=text_preview,
        )

        try:
            raw = self.invoke_llm(prompt, task_type="reasoning")
            json_str = extract_first_json(raw)
            if json_str:
                data = json.loads(json_str)
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

        return DowAgentResult(
            job_id=payload.job_id,
            agent_name=self.agent_name,
            stage_id=payload.stage_id,
            status="completed",
            json_data=data,
        )
