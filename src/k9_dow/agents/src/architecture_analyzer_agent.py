# SPDX-License-Identifier: Apache-2.0
# DoW Architecture Workbench — ArchitectureAnalyzerAgent (SBB)

from typing import Any, Dict, Optional

from k9_aif_abb.k9_core.agent.base_agent import BaseAgent
from k9_aif_abb.k9_inference.models.inference_request import InferenceRequest
from k9_aif_abb.k9_utils.llm_invoke import llm_invoke


class ArchitectureAnalyzerAgent(BaseAgent):
    layer = "DoW ArchitectureAnalyzer SBB"

    def __init__(self, config: Optional[Dict[str, Any]] = None, monitor=None, **kwargs):
        super().__init__(config or {}, monitor=monitor, **kwargs)

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        source = payload.get("source_markdown") or ""
        prior = payload.get("prior_outputs") or {}
        prior_text = "\n".join(prior.values()) if prior else ""

        prompt = (
            f"Role: {self.config.get('role', 'DoD Architecture Fitness Analyst')}\n"
            f"Goal: {self.config.get('goal', 'Analyze architecture against stated objectives and mission needs')}\n\n"
            "## Grounding Rules\n"
            "Use only the source document and approved prior-stage outputs.\n"
            "Do not invent facts. If evidence is missing, write: NOT PROVIDED IN SOURCE.\n"
            "Include short source evidence snippets. Keep tone neutral, government-review-ready.\n\n"
            "## Task\n"
            "Analyze the architecture against stated objectives and mission needs.\n\n"
            "Produce the following sections:\n"
            "## Objective Alignment\n"
            "For each objective, assess whether the architecture data supports it.\n"
            "Rate alignment: Strong / Partial / Weak / Not Addressed.\n\n"
            "## Architecture Gaps\n"
            "Identify gaps between objectives and architecture elements.\n\n"
            "## Fitness Assessment\n"
            "Overall fitness of the architecture for the stated mission context.\n\n"
            "## Recommendations\n"
            "Evidence-based recommendations to close gaps.\n\n"
            "If not found: NOT PROVIDED IN SOURCE\n\n"
            f"## Source Document\n{source[:6000]}\n"
        )
        if prior_text:
            prompt += f"\n## Prior Outputs\n{prior_text[:4000]}\n"

        req = InferenceRequest(
            prompt=prompt,
            task_type=self.config.get("model", "reasoning"),
            metadata={"agent": "ArchitectureAnalyzerAgent"},
        )
        resp = llm_invoke(self.config, req)
        output = resp.output.strip()

        self.publish_event({"type": "AgentCompleted", "agent": "ArchitectureAnalyzerAgent"})
        return {"agent": "ArchitectureAnalyzerAgent", "output": output}
