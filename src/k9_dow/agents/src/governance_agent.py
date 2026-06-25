# SPDX-License-Identifier: Apache-2.0
# DoW Architecture Workbench — GovernanceAgent (SBB)

import json
import logging
from typing import Any, Dict, Optional

from k9_aif_abb.k9_core.agent.base_agent import BaseAgent
from k9_aif_abb.k9_inference.models.inference_request import InferenceRequest
from k9_aif_abb.k9_utils.llm_invoke import llm_invoke

log = logging.getLogger(__name__)

GOVERNANCE_RULES = """\
G1. Use only information explicitly present in the source document or prior approved stage outputs.
G2. If a requested element is not supported, output NOT PROVIDED IN SOURCE.
G3. Do not invent stakeholders, capabilities, systems, services, interfaces, constraints, risks, requirements, KPPs, KSAs, KURs, or timelines.
G4. Include evidence snippets where possible.
G5. Maintain neutral DoD/government-review-ready tone.
G6. Do not mention internal implementation frameworks in generated domain reports.
G7. Mark uncertainty explicitly.
G8. Preserve traceability from source text to derived stage output.
G9. Separate extracted facts from analysis.
G10. Send outputs through governance validation before persistence.
"""


class GovernanceAgent(BaseAgent):
    """
    Reviews stage outputs against governance rules.

    Checks for invented content, missing citations, and compliance
    with DoD evidence-grounding requirements.
    """

    layer = "DoW Governance SBB"

    def __init__(self, config: Optional[Dict[str, Any]] = None, monitor=None, **kwargs):
        super().__init__(config or {}, monitor=monitor, **kwargs)

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        prior = payload.get("prior_outputs") or {}
        prior_text = "\n\n".join(prior.values()) if prior else ""

        if not prior_text.strip():
            self.publish_event({"type": "AgentCompleted", "agent": "GovernanceAgent"})
            return {
                "agent": "GovernanceAgent",
                "output": "## Governance Review\n\nNo prior outputs to review.\n\n**Status:** pass",
            }

        prompt = (
            f"Role: {self.config.get('role', 'DoD Architecture Governance Reviewer')}\n"
            f"Goal: {self.config.get('goal', 'Review stage outputs against governance rules')}\n\n"
            "## Task\n"
            "Review the following stage outputs against these governance rules:\n\n"
            f"{GOVERNANCE_RULES}\n\n"
            "Return JSON:\n"
            '{"status": "pass|warn|block", "findings": [{"severity": "info|warning|error|blocker", '
            '"rule_id": "G1-G10", "message": "...", "evidence": "..."}], "summary": "..."}\n\n'
            f"## Stage Outputs\n{prior_text[:6000]}\n"
        )

        try:
            req = InferenceRequest(
                prompt=prompt,
                task_type=self.config.get("model", "reasoning"),
                metadata={"agent": "GovernanceAgent"},
            )
            resp = llm_invoke(self.config, req)
            raw = resp.output.strip()

            # Try to extract JSON from response
            json_start = raw.find("{")
            json_end = raw.rfind("}") + 1
            if json_start >= 0 and json_end > json_start:
                data = json.loads(raw[json_start:json_end])
            else:
                data = {
                    "status": "pass",
                    "findings": [],
                    "summary": "Governance review completed (no JSON returned)",
                }
        except Exception as exc:
            log.warning("[GovernanceAgent] LLM review failed: %s", exc)
            data = {
                "status": "warn",
                "findings": [],
                "summary": f"Governance review failed: {exc}",
            }

        status = data.get("status", "pass")
        md = f"## Governance Review\n\n**Status:** {status}\n\n{data.get('summary', '')}\n"
        if data.get("findings"):
            md += "\n### Findings\n"
            for f in data["findings"]:
                md += f"- **[{f.get('severity', 'info')}] {f.get('rule_id', '')}:** {f.get('message', '')}\n"

        self.publish_event({"type": "AgentCompleted", "agent": "GovernanceAgent"})
        return {"agent": "GovernanceAgent", "output": md}
