# SPDX-License-Identifier: Apache-2.0
# DoW Architecture Workbench — DataRequirementsAgent (SBB)

from typing import Any, Dict, Optional

from k9_aif_abb.k9_core.agent.base_agent import BaseAgent
from k9_aif_abb.k9_inference.models.inference_request import InferenceRequest
from k9_aif_abb.k9_utils.llm_invoke import llm_invoke


class DataRequirementsAgent(BaseAgent):
    layer = "DoW DataRequirements SBB"

    def __init__(self, config: Optional[Dict[str, Any]] = None, monitor=None, **kwargs):
        super().__init__(config or {}, monitor=monitor, **kwargs)

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        source = payload.get("source_markdown") or ""
        prior = payload.get("prior_outputs") or {}
        prior_text = "\n".join(prior.values()) if prior else ""

        prompt = (
            f"Role: {self.config.get('role', 'Architecture Data Requirements Analyst')}\n"
            f"Goal: {self.config.get('goal', 'Identify required architecture data from source and prior outputs')}\n\n"
            "## Grounding Rules\n"
            "Use only the source document and approved prior-stage outputs.\n"
            "Do not invent facts. If evidence is missing, write: NOT PROVIDED IN SOURCE.\n"
            "Include short source evidence snippets. Keep tone neutral, government-review-ready.\n\n"
            "## Task\n"
            "Identify the required architecture data from the source document "
            "and prior stage outputs.\n"
            "For each data requirement provide:\n"
            "- Data element name\n"
            "- Description\n"
            "- DoDAF view mapping (which DoDAF view this data supports: "
            "OV-1, OV-2, OV-5, SV-1, SV-4, CV-2, etc.)\n"
            "- Data source (where this data originates or should be collected)\n"
            "- Priority (critical/important/nice-to-have)\n"
            "- Verbatim evidence from the source\n\n"
            "If not found: NOT PROVIDED IN SOURCE\n\n"
            "Return Markdown report and JSON:\n"
            '{"data_requirements": [{"name": "...", "description": "...", '
            '"view_mapping": ["..."], "data_source": "...", "priority": "...", '
            '"evidence": "..."}]}\n\n'
            f"## Source Document\n{source[:6000]}\n"
        )
        if prior_text:
            prompt += f"\n## Prior Outputs\n{prior_text[:4000]}\n"

        req = InferenceRequest(
            prompt=prompt,
            task_type=self.config.get("model", "reasoning"),
            metadata={"agent": "DataRequirementsAgent"},
        )
        resp = llm_invoke(self.config, req)
        output = resp.output.strip()

        self.publish_event({"type": "AgentCompleted", "agent": "DataRequirementsAgent"})
        return {"agent": "DataRequirementsAgent", "output": output}
