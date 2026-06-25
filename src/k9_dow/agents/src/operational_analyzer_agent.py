# SPDX-License-Identifier: Apache-2.0
# DoW Architecture Workbench — OperationalAnalyzerAgent (SBB)

from typing import Any, Dict, Optional

from k9_aif_abb.k9_core.agent.base_agent import BaseAgent
from k9_aif_abb.k9_inference.models.inference_request import InferenceRequest
from k9_aif_abb.k9_utils.llm_invoke import llm_invoke


class OperationalAnalyzerAgent(BaseAgent):
    layer = "DoW OperationalAnalyzer SBB"

    def __init__(self, config: Optional[Dict[str, Any]] = None, monitor=None, **kwargs):
        super().__init__(config or {}, monitor=monitor, **kwargs)

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        source = payload.get("source_markdown") or ""
        prior = payload.get("prior_outputs") or {}
        prior_text = "\n".join(prior.values()) if prior else ""

        prompt = (
            f"Role: {self.config.get('role', 'Operational Architecture Analyst')}\n"
            f"Goal: {self.config.get('goal', 'Analyze operational architecture for mission alignment')}\n\n"
            "## Grounding Rules\n"
            "Use only the source document and approved prior-stage outputs.\n"
            "Do not invent facts. If evidence is missing, write: NOT PROVIDED IN SOURCE.\n"
            "Include short source evidence snippets. Keep tone neutral, government-review-ready.\n\n"
            "## Task\n"
            "Analyze the operational architecture for mission alignment.\n\n"
            "Produce the following sections:\n\n"
            "## Mission Alignment Assessment\n"
            "For each operational activity, assess alignment to the stated mission.\n"
            "| Activity | Mission Need | Alignment | Evidence |\n"
            "Alignment: Direct / Indirect / Not Aligned / Unclear.\n\n"
            "## Operational Strengths\n"
            "List well-supported operational areas with strong evidence:\n"
            "- Clear performer assignments\n"
            "- Well-defined information exchanges\n"
            "- Complete activity decompositions\n\n"
            "## Operational Weaknesses\n"
            "List operational areas with deficiencies:\n"
            "- Activities without assigned performers\n"
            "- Missing or undefined information exchanges\n"
            "- Incomplete process flows\n\n"
            "## Operational Gaps\n"
            "Identify missing operational elements:\n"
            "- Mission needs without supporting activities\n"
            "- Activities without supporting systems\n"
            "- Disconnected operational nodes\n\n"
            "## Operational Risk Summary\n"
            "Summarize key operational risks based on the analysis.\n\n"
            "If not found: NOT PROVIDED IN SOURCE\n\n"
            f"## Source Document\n{source[:6000]}\n"
        )
        if prior_text:
            prompt += f"\n## Prior Outputs\n{prior_text[:4000]}\n"

        req = InferenceRequest(
            prompt=prompt,
            task_type=self.config.get("model", "reasoning"),
            metadata={"agent": "OperationalAnalyzerAgent"},
        )
        resp = llm_invoke(self.config, req)
        output = resp.output.strip()

        self.publish_event({"type": "AgentCompleted", "agent": "OperationalAnalyzerAgent"})
        return {"agent": "OperationalAnalyzerAgent", "output": output}
