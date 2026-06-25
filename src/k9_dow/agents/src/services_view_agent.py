# SPDX-License-Identifier: Apache-2.0
# DoW Architecture Workbench — ServicesViewAgent (SBB)

from typing import Any, Dict, Optional

from k9_aif_abb.k9_core.agent.base_agent import BaseAgent
from k9_aif_abb.k9_inference.models.inference_request import InferenceRequest
from k9_aif_abb.k9_utils.llm_invoke import llm_invoke


class ServicesViewAgent(BaseAgent):
    layer = "DoW ServicesView SBB"

    def __init__(self, config: Optional[Dict[str, Any]] = None, monitor=None, **kwargs):
        super().__init__(config or {}, monitor=monitor, **kwargs)

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        source = payload.get("source_markdown") or ""
        prior = payload.get("prior_outputs") or {}
        prior_text = "\n".join(prior.values()) if prior else ""

        prompt = (
            f"Role: {self.config.get('role', 'Service Architecture View Specialist')}\n"
            f"Goal: {self.config.get('goal', 'Structure service-level architecture views from extracted data')}\n\n"
            "## Grounding Rules\n"
            "Use only the source document and approved prior-stage outputs.\n"
            "Do not invent facts. If evidence is missing, write: NOT PROVIDED IN SOURCE.\n"
            "Include short source evidence snippets. Keep tone neutral, government-review-ready.\n\n"
            "## Task\n"
            "Structure service-level architecture views from the extracted data.\n\n"
            "Produce the following sections:\n"
            "## SvcV-1 -- Service Context\n"
            "Describe service dependencies and interactions.\n"
            "Use a table: Service | Provider | Consumer | Interface | Protocol.\n\n"
            "## SvcV-3a -- System-Service Matrix\n"
            "Map which systems host or provide which services.\n"
            "Use a table: System | Service | Relationship (hosts/consumes/provides).\n\n"
            "## SvcV-4 -- Service Functionality\n"
            "Map service functions and their descriptions.\n"
            "Use a table: Service | Function | Description | Input | Output.\n\n"
            "## Service Dependency Chain\n"
            "Identify critical service dependency chains and single points of failure.\n\n"
            "Cross-reference with system views and operational activities from prior outputs.\n"
            "If not found: NOT PROVIDED IN SOURCE\n\n"
            f"## Source Document\n{source[:6000]}\n"
        )
        if prior_text:
            prompt += f"\n## Prior Outputs\n{prior_text[:4000]}\n"

        req = InferenceRequest(
            prompt=prompt,
            task_type=self.config.get("model", "reasoning"),
            metadata={"agent": "ServicesViewAgent"},
        )
        resp = llm_invoke(self.config, req)
        output = resp.output.strip()

        self.publish_event({"type": "AgentCompleted", "agent": "ServicesViewAgent"})
        return {"agent": "ServicesViewAgent", "output": output}
