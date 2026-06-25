# SPDX-License-Identifier: Apache-2.0
# DoW Architecture Workbench — PresentationAgent (SBB)

from typing import Any, Dict, Optional

from k9_aif_abb.k9_core.agent.base_agent import BaseAgent
from k9_aif_abb.k9_inference.models.inference_request import InferenceRequest
from k9_aif_abb.k9_utils.llm_invoke import llm_invoke


class PresentationAgent(BaseAgent):
    layer = "DoW Presentation SBB"

    def __init__(self, config: Optional[Dict[str, Any]] = None, monitor=None, **kwargs):
        super().__init__(config or {}, monitor=monitor, **kwargs)

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        source = payload.get("source_markdown") or ""
        prior = payload.get("prior_outputs") or {}
        prior_text = "\n".join(prior.values()) if prior else ""

        prompt = (
            f"Role: {self.config.get('role', 'Senior Architecture Presentation Specialist')}\n"
            f"Goal: {self.config.get('goal', 'Build a decision-ready presentation package from all prior outputs')}\n\n"
            "## Grounding Rules\n"
            "Use only the source document and approved prior-stage outputs.\n"
            "Do not invent facts. Do NOT add new analysis. Compile and organize only.\n"
            "Reference evidence from prior outputs.\n\n"
            "## Task\n"
            "Build a decision-ready presentation package from all prior outputs.\n\n"
            "Use this executive briefing format:\n\n"
            "# Architecture Decision Package\n\n"
            "## 1. Executive Summary\n"
            "Two-paragraph overview: what was analyzed, key conclusions.\n\n"
            "## 2. Mission Context and Objectives\n"
            "Restate the mission context and architecture objectives.\n\n"
            "## 3. Key Findings\n"
            "Organize by domain:\n"
            "### Capability Findings\n"
            "### Operational Findings\n"
            "### System/Service Findings\n"
            "### Risk Findings\n\n"
            "## 4. Gap Analysis Summary\n"
            "Consolidated view of all identified gaps, ordered by severity.\n\n"
            "## 5. Architecture Decision Matrix\n"
            "| Decision Area | Options | Recommendation | Rationale |\n\n"
            "## 6. Action Items (Top 10)\n"
            "Prioritized list of the most critical action items.\n\n"
            "## 7. Readiness Assessment\n"
            "Overall architecture readiness: Ready / Conditionally Ready / Not Ready.\n"
            "Justify with evidence from prior outputs.\n\n"
            "## 8. Next Steps\n"
            "Recommended next steps for the architecture development effort.\n\n"
            "If not found: NOT PROVIDED IN SOURCE\n\n"
            f"## Source Document\n{source[:1000]}\n\n"
            f"## Prior Outputs\n{prior_text}\n"
        )

        req = InferenceRequest(
            prompt=prompt,
            task_type=self.config.get("model", "general"),
            metadata={"agent": "PresentationAgent"},
        )
        resp = llm_invoke(self.config, req)
        output = resp.output.strip()

        self.publish_event({"type": "AgentCompleted", "agent": "PresentationAgent"})
        return {"agent": "PresentationAgent", "output": output}
