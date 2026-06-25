# SPDX-License-Identifier: Apache-2.0
# DoW Architecture Workbench — PainPointExtractorAgent (SBB)

from typing import Any, Dict, Optional

from k9_aif_abb.k9_core.agent.base_agent import BaseAgent
from k9_aif_abb.k9_inference.models.inference_request import InferenceRequest
from k9_aif_abb.k9_utils.llm_invoke import llm_invoke


class PainPointExtractorAgent(BaseAgent):
    layer = "DoW PainPointExtractor SBB"

    def __init__(self, config: Optional[Dict[str, Any]] = None, monitor=None, **kwargs):
        super().__init__(config or {}, monitor=monitor, **kwargs)

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        source = payload.get("source_markdown") or ""
        prior = payload.get("prior_outputs") or {}
        prior_text = "\n".join(prior.values()) if prior else ""

        prompt = (
            f"Role: {self.config.get('role', 'Pain Point and Operational Problem Analyst')}\n"
            f"Goal: {self.config.get('goal', 'Extract pain points, challenges, and operational problems')}\n\n"
            "## Grounding Rules\n"
            "Use only the source document and approved prior-stage outputs.\n"
            "Do not invent facts. If evidence is missing, write: NOT PROVIDED IN SOURCE.\n"
            "Include short source evidence snippets. Keep tone neutral, government-review-ready.\n\n"
            "## Task\n"
            "Extract all pain points, challenges, and operational problems.\n"
            "For each provide:\n"
            "- Description\n"
            "- Category (operational/technical/organizational/resource)\n"
            "- Impact\n"
            "- Verbatim evidence\n\n"
            "Then write an OV-1 style problem framing paragraph.\n\n"
            "If no pain points found, write: NOT PROVIDED IN SOURCE\n\n"
            "Return Markdown report and JSON:\n"
            '{"pain_points": [{"description": "...", "category": "...", "impact": "...", "evidence": "..."}], '
            '"problem_framing": "..."}\n\n'
            f"## Source Document\n{source[:6000]}\n"
        )
        if prior_text:
            prompt += f"\n## Prior Outputs\n{prior_text[:4000]}\n"

        req = InferenceRequest(
            prompt=prompt,
            task_type=self.config.get("model", "reasoning"),
            metadata={"agent": "PainPointExtractorAgent"},
        )
        resp = llm_invoke(self.config, req)
        output = resp.output.strip()

        self.publish_event({"type": "AgentCompleted", "agent": "PainPointExtractorAgent"})
        return {"agent": "PainPointExtractorAgent", "output": output}
