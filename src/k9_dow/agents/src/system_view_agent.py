# SPDX-License-Identifier: Apache-2.0
# DoW Architecture Workbench — SystemViewAgent (SBB)

from typing import Any, Dict, Optional

from k9_aif_abb.k9_core.agent.base_agent import BaseAgent
from k9_aif_abb.k9_inference.models.inference_request import InferenceRequest
from k9_aif_abb.k9_utils.llm_invoke import llm_invoke


class SystemViewAgent(BaseAgent):
    layer = "DoW SystemView SBB"

    def __init__(self, config: Optional[Dict[str, Any]] = None, monitor=None, **kwargs):
        super().__init__(config or {}, monitor=monitor, **kwargs)

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        source = payload.get("source_markdown") or ""
        prior = payload.get("prior_outputs") or {}
        prior_text = "\n".join(prior.values()) if prior else ""

        prompt = (
            f"Role: {self.config.get('role', 'System Architecture View Specialist')}\n"
            f"Goal: {self.config.get('goal', 'Structure system-level architecture views from extracted data')}\n\n"
            "## Grounding Rules\n"
            "Use only the source document and approved prior-stage outputs.\n"
            "Do not invent facts. If evidence is missing, write: NOT PROVIDED IN SOURCE.\n"
            "Include short source evidence snippets. Keep tone neutral, government-review-ready.\n\n"
            "## Task\n"
            "Structure system-level architecture views from the extracted data.\n\n"
            "Produce the following sections:\n"
            "## SV-1 -- System Interface Description\n"
            "List each system, its interfaces, and connected systems.\n"
            "Use a table: System | Interface | Connected To | Protocol.\n\n"
            "## SV-2 -- System Resource Flow\n"
            "Map resource flows between systems.\n"
            "Use a table: Source System | Resource | Destination System.\n\n"
            "## SV-4 -- System Functionality\n"
            "Map system functions to the systems that perform them.\n"
            "Use a table: System | Function | Description.\n\n"
            "Cross-reference with operational activities from prior outputs.\n"
            "If not found: NOT PROVIDED IN SOURCE\n\n"
            f"## Source Document\n{source[:6000]}\n"
        )
        if prior_text:
            prompt += f"\n## Prior Outputs\n{prior_text[:4000]}\n"

        req = InferenceRequest(
            prompt=prompt,
            task_type=self.config.get("model", "reasoning"),
            metadata={"agent": "SystemViewAgent"},
        )
        resp = llm_invoke(self.config, req)
        output = resp.output.strip()

        self.publish_event({"type": "AgentCompleted", "agent": "SystemViewAgent"})
        return {"agent": "SystemViewAgent", "output": output}
