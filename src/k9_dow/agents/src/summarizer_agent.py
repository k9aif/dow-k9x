# SPDX-License-Identifier: Apache-2.0
# DoW Architecture Workbench — SummarizerAgent (SBB)

from typing import Any, Dict, Optional

from k9_aif_abb.k9_core.agent.base_agent import BaseAgent
from k9_aif_abb.k9_inference.models.inference_request import InferenceRequest
from k9_aif_abb.k9_utils.llm_invoke import llm_invoke


class SummarizerAgent(BaseAgent):
    layer = "DoW Summarizer SBB"

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
            else "No prior outputs."
        )

        prompt = (
            f"Role: {self.config.get('role', 'Technical Report Writer')}\n"
            f"Goal: {self.config.get('goal', 'Compile agent outputs into a structured stage report')}\n\n"
            "## Grounding Rules\n"
            "Use only the source document and approved prior-stage outputs.\n"
            "Do not invent facts. Preserve all citations.\n\n"
            "## Task\n"
            "Compile the following agent outputs into a structured stage report.\n\n"
            "Use this format:\n"
            "# Stage Report\n"
            "## Source Summary\n"
            "## Extracted Findings\n"
            "## Analysis\n"
            "## Evidence / Citations\n"
            "## Unsupported or Missing Information\n"
            "## Next Steps\n\n"
            "Do not add new analysis — only compile and organize.\n"
            "Preserve all citations.\n\n"
            f"## Source Document\n{source[:1000]}\n\n"
            f"## Prior Outputs\n{prior_text}\n"
        )

        req = InferenceRequest(
            prompt=prompt,
            task_type=self.config.get("model", "general"),
            metadata={"agent": "SummarizerAgent"},
        )
        resp = llm_invoke(self.config, req)
        output = resp.output.strip()

        self.publish_event({"type": "AgentCompleted", "agent": "SummarizerAgent"})
        return {"agent": "SummarizerAgent", "output": output}
