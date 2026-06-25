# SPDX-License-Identifier: Apache-2.0
# DoW Architecture Workbench — VerificationAgent (SBB)

from typing import Any, Dict, Optional

from k9_aif_abb.k9_core.agent.base_agent import BaseAgent
from k9_aif_abb.k9_inference.models.inference_request import InferenceRequest
from k9_aif_abb.k9_utils.llm_invoke import llm_invoke


class VerificationAgent(BaseAgent):
    layer = "DoW Verification SBB"

    def __init__(self, config: Optional[Dict[str, Any]] = None, monitor=None, **kwargs):
        super().__init__(config or {}, monitor=monitor, **kwargs)

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        source = payload.get("source_markdown") or ""
        prior = payload.get("prior_outputs") or {}
        prior_text = "\n".join(prior.values()) if prior else ""

        prompt = (
            f"Role: {self.config.get('role', 'Architecture Verification Specialist')}\n"
            f"Goal: {self.config.get('goal', 'Perform cross-view consistency and completeness checks')}\n\n"
            "## Grounding Rules\n"
            "Use only the source document and approved prior-stage outputs.\n"
            "Do not invent facts. If evidence is missing, write: NOT PROVIDED IN SOURCE.\n"
            "Include short source evidence snippets. Keep tone neutral, government-review-ready.\n\n"
            "## Task\n"
            "Perform cross-view consistency and completeness checks.\n\n"
            "Produce the following sections:\n\n"
            "## Cross-View Consistency\n"
            "Check that entities referenced in one viewpoint exist and are\n"
            "consistently named in related viewpoints.\n"
            "| Element | View A | View B | Status | Issue |\n"
            "Status: Consistent / Inconsistent / Missing.\n\n"
            "## Traceability Validation\n"
            "Verify complete traceability chains:\n"
            "- Mission Need -> Capability -> System/Service\n"
            "- Operational Activity -> System Function -> Service\n"
            "Flag broken chains.\n\n"
            "## Orphan Elements\n"
            "List architecture elements that appear in only one viewpoint\n"
            "with no cross-references.\n\n"
            "## Completeness Assessment\n"
            "For each viewpoint, assess data completeness:\n"
            "| Viewpoint | Elements Found | Completeness | Missing |\n\n"
            "## Consistency Scorecard\n"
            "Provide an overall consistency score (0-100) with rationale.\n\n"
            "If not found: NOT PROVIDED IN SOURCE\n\n"
            f"## Source Document\n{source[:6000]}\n"
        )
        if prior_text:
            prompt += f"\n## Prior Outputs\n{prior_text[:4000]}\n"

        req = InferenceRequest(
            prompt=prompt,
            task_type=self.config.get("model", "reasoning"),
            metadata={"agent": "VerificationAgent"},
        )
        resp = llm_invoke(self.config, req)
        output = resp.output.strip()

        self.publish_event({"type": "AgentCompleted", "agent": "VerificationAgent"})
        return {"agent": "VerificationAgent", "output": output}
