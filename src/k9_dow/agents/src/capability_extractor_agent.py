# SPDX-License-Identifier: Apache-2.0
# DoW Architecture Workbench — CapabilityExtractorAgent (SBB)

from typing import Any, Dict, Optional

from k9_aif_abb.k9_core.agent.base_agent import BaseAgent
from k9_aif_abb.k9_inference.models.inference_request import InferenceRequest
from k9_aif_abb.k9_utils.llm_invoke import llm_invoke


class CapabilityExtractorAgent(BaseAgent):
    layer = "DoW CapabilityExtractor SBB"

    def __init__(self, config: Optional[Dict[str, Any]] = None, monitor=None, **kwargs):
        super().__init__(config or {}, monitor=monitor, **kwargs)

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        source = payload.get("source_markdown") or ""
        prior = payload.get("prior_outputs") or {}
        prior_text = "\n".join(prior.values()) if prior else ""

        prompt = (
            f"Role: {self.config.get('role', 'Capability Analyst')}\n"
            f"Goal: {self.config.get('goal', 'Extract all capability references from source documents')}\n\n"
            "## Grounding Rules\n"
            "Use only the source document and approved prior-stage outputs.\n"
            "Do not invent facts. If evidence is missing, write: NOT PROVIDED IN SOURCE.\n"
            "Include short source evidence snippets. Keep tone neutral, government-review-ready.\n\n"
            "## Task\n"
            "Extract all capability references from the source document.\n"
            "For each capability provide:\n"
            "- Capability name\n"
            "- Description\n"
            "- Scope relation (which scope domain it maps to)\n"
            "- Associated operational activities (if stated)\n"
            "- Verbatim evidence from the source\n\n"
            "Align to CV-2 style capability taxonomy where possible.\n\n"
            "If not found: NOT PROVIDED IN SOURCE\n\n"
            "Return Markdown report and JSON:\n"
            '{"capabilities": [{"name": "...", "description": "...", '
            '"scope_relation": "...", "activities": ["..."], "evidence": "..."}]}\n\n'
            f"## Source Document\n{source[:6000]}\n"
        )
        if prior_text:
            prompt += f"\n## Prior Outputs\n{prior_text[:4000]}\n"

        req = InferenceRequest(
            prompt=prompt,
            task_type=self.config.get("model", "reasoning"),
            metadata={"agent": "CapabilityExtractorAgent"},
        )
        resp = llm_invoke(self.config, req)
        output = resp.output.strip()

        self.publish_event({"type": "AgentCompleted", "agent": "CapabilityExtractorAgent"})
        return {"agent": "CapabilityExtractorAgent", "output": output}
