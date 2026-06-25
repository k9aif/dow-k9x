# SPDX-License-Identifier: Apache-2.0
# DoW Architecture Workbench — MissionAssessmentAgent (SBB)

from typing import Any, Dict, Optional

from k9_aif_abb.k9_core.agent.base_agent import BaseAgent
from k9_aif_abb.k9_inference.models.inference_request import InferenceRequest
from k9_aif_abb.k9_utils.llm_invoke import llm_invoke


class MissionAssessmentAgent(BaseAgent):
    layer = "DoW MissionAssessment SBB"

    def __init__(self, config: Optional[Dict[str, Any]] = None, monitor=None, **kwargs):
        super().__init__(config or {}, monitor=monitor, **kwargs)

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        source = payload.get("source_markdown") or ""
        prior = payload.get("prior_outputs") or {}
        prior_text = "\n".join(prior.values()) if prior else ""

        prompt = (
            f"Role: {self.config.get('role', 'Mission Context Analyst')}\n"
            f"Goal: {self.config.get('goal', 'Assess mission context from source documents')}\n\n"
            "## Grounding Rules\n"
            "Use only the source document and approved prior-stage outputs.\n"
            "Do not invent facts. If evidence is missing, write: NOT PROVIDED IN SOURCE.\n"
            "Include short source evidence snippets. Keep tone neutral, government-review-ready.\n\n"
            "## Task\n"
            "Assess the mission context from the source document:\n"
            "1. Mission context summary\n"
            "2. Operational environment description\n"
            "3. Mission threads or operational threads (if present)\n"
            "4. Operational relevance assessment\n\n"
            "Cite evidence for all claims.\n"
            "If no mission context found, write: NOT PROVIDED IN SOURCE\n\n"
            f"## Source Document\n{source[:6000]}\n"
        )
        if prior_text:
            prompt += f"\n## Prior Outputs\n{prior_text[:4000]}\n"

        req = InferenceRequest(
            prompt=prompt,
            task_type=self.config.get("model", "reasoning"),
            metadata={"agent": "MissionAssessmentAgent"},
        )
        resp = llm_invoke(self.config, req)
        output = resp.output.strip()

        self.publish_event({"type": "AgentCompleted", "agent": "MissionAssessmentAgent"})
        return {"agent": "MissionAssessmentAgent", "output": output}
