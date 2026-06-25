# SPDX-License-Identifier: Apache-2.0
# DoW Architecture Workbench — F2PIntentAgent (SBB)

from typing import Any, Dict, Optional

from k9_aif_abb.k9_core.agent.base_agent import BaseAgent
from k9_aif_abb.k9_inference.models.inference_request import InferenceRequest
from k9_aif_abb.k9_utils.llm_invoke import llm_invoke


class F2PIntentAgent(BaseAgent):
    layer = "DoW F2PIntent SBB"

    def __init__(self, config: Optional[Dict[str, Any]] = None, monitor=None, **kwargs):
        super().__init__(config or {}, monitor=monitor, **kwargs)

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        source = payload.get("source_markdown") or ""
        prior = payload.get("prior_outputs") or {}
        prior_text = (
            "\n\n---\n\n".join(
                f"### {name}\n{text}" for name, text in prior.items()
            )
            if prior
            else "No prior outputs available."
        )

        prompt = (
            f"Role: {self.config.get('role', 'Fit-for-Purpose Intent Analyst')}\n"
            f"Goal: {self.config.get('goal', 'Synthesize prior outputs into a Fit-for-Purpose intent statement')}\n\n"
            "## Grounding Rules\n"
            "Use only the source document and approved prior-stage outputs.\n"
            "Do not invent facts. If evidence is missing, write: NOT PROVIDED IN SOURCE.\n"
            "Include short source evidence snippets. Keep tone neutral, government-review-ready.\n\n"
            "## Task\n"
            "Based on the prior agent outputs below, create a Fit-for-Purpose "
            "intent statement that synthesizes:\n"
            "1. Key stakeholders and their concerns\n"
            "2. Core pain points and operational problems\n"
            "3. Stated objectives and desired outcomes\n"
            "4. Mission context and relevance\n\n"
            "Then provide a readiness assessment:\n"
            "- READY: sufficient for full architecture development\n"
            "- NEEDS_ENRICHMENT: viable but needs additional context\n"
            "- INSUFFICIENT: not enough information for architecture work\n\n"
            "Use only information from prior outputs. Do not invent.\n\n"
            f"## Source Document\n{source[:2000]}\n\n"
            f"## Prior Outputs\n{prior_text}\n"
        )

        req = InferenceRequest(
            prompt=prompt,
            task_type=self.config.get("model", "reasoning"),
            metadata={"agent": "F2PIntentAgent"},
        )
        resp = llm_invoke(self.config, req)
        output = resp.output.strip()

        self.publish_event({"type": "AgentCompleted", "agent": "F2PIntentAgent"})
        return {"agent": "F2PIntentAgent", "output": output}
