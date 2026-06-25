# SPDX-License-Identifier: Apache-2.0
# DoW Architecture Workbench — RequirementAgent (SBB)

from typing import Any, Dict, Optional

from k9_aif_abb.k9_core.agent.base_agent import BaseAgent
from k9_aif_abb.k9_inference.models.inference_request import InferenceRequest
from k9_aif_abb.k9_utils.llm_invoke import llm_invoke


class RequirementAgent(BaseAgent):
    layer = "DoW Requirement SBB"

    def __init__(self, config: Optional[Dict[str, Any]] = None, monitor=None, **kwargs):
        super().__init__(config or {}, monitor=monitor, **kwargs)

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        source = payload.get("source_markdown") or ""
        prior = payload.get("prior_outputs") or {}
        prior_text = "\n".join(prior.values()) if prior else ""

        prompt = (
            f"Role: {self.config.get('role', 'Requirements Engineer')}\n"
            f"Goal: {self.config.get('goal', 'Extract and structure requirements from analysis outputs')}\n\n"
            "## Grounding Rules\n"
            "Use only the source document and approved prior-stage outputs.\n"
            "Do not invent facts. If evidence is missing, write: NOT PROVIDED IN SOURCE.\n"
            "Include short source evidence snippets. Keep tone neutral, government-review-ready.\n\n"
            "## Task\n"
            "Extract and structure requirements from the analysis outputs.\n"
            "For each requirement provide:\n"
            "- Requirement ID (REQ-NNN)\n"
            "- Statement\n"
            "- Type (functional/non-functional/interface/performance)\n"
            "- Priority (critical/high/medium/low)\n"
            "- Traces to (which objective, capability, or gap)\n"
            "- Verbatim evidence or rationale\n\n"
            "If not found: NOT PROVIDED IN SOURCE\n\n"
            "Return Markdown report and JSON:\n"
            '{"requirements": [{"id": "REQ-001", "statement": "...", '
            '"type": "...", "priority": "...", "traces_to": "...", "evidence": "..."}]}\n\n'
            f"## Source Document\n{source[:6000]}\n"
        )
        if prior_text:
            prompt += f"\n## Prior Outputs\n{prior_text[:4000]}\n"

        req = InferenceRequest(
            prompt=prompt,
            task_type=self.config.get("model", "reasoning"),
            metadata={"agent": "RequirementAgent"},
        )
        resp = llm_invoke(self.config, req)
        output = resp.output.strip()

        self.publish_event({"type": "AgentCompleted", "agent": "RequirementAgent"})
        return {"agent": "RequirementAgent", "output": output}
