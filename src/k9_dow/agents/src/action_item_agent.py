# SPDX-License-Identifier: Apache-2.0
# DoW Architecture Workbench — ActionItemAgent (SBB)

from typing import Any, Dict, Optional

from k9_aif_abb.k9_core.agent.base_agent import BaseAgent
from k9_aif_abb.k9_inference.models.inference_request import InferenceRequest
from k9_aif_abb.k9_utils.llm_invoke import llm_invoke


class ActionItemAgent(BaseAgent):
    layer = "DoW ActionItem SBB"

    def __init__(self, config: Optional[Dict[str, Any]] = None, monitor=None, **kwargs):
        super().__init__(config or {}, monitor=monitor, **kwargs)

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        source = payload.get("source_markdown") or ""
        prior = payload.get("prior_outputs") or {}
        prior_text = "\n".join(prior.values()) if prior else ""

        prompt = (
            f"Role: {self.config.get('role', 'Architecture Action Planning Specialist')}\n"
            f"Goal: {self.config.get('goal', 'Generate prioritized action items from analysis findings')}\n\n"
            "## Grounding Rules\n"
            "Use only the source document and approved prior-stage outputs.\n"
            "Do not invent facts. If evidence is missing, write: NOT PROVIDED IN SOURCE.\n"
            "Include short source evidence snippets. Keep tone neutral, government-review-ready.\n\n"
            "## Task\n"
            "Generate prioritized action items from all analysis findings.\n\n"
            "Review all prior outputs for:\n"
            "- Capability gaps\n"
            "- Operational weaknesses\n"
            "- Architecture alignment issues\n"
            "- Risk findings\n"
            "- Cross-view consistency issues\n"
            "- Missing evidence or data gaps\n\n"
            "For each action item provide:\n"
            "- Action ID (ACT-NNN)\n"
            "- Title\n"
            "- Description\n"
            "- Priority (critical/high/medium/low)\n"
            "- Category (architecture/operational/system/governance)\n"
            "- Responsible viewpoint owner\n"
            "- Originating finding\n\n"
            "Order by priority (critical first), then by category.\n\n"
            "If no findings to act on: NOT PROVIDED IN SOURCE\n\n"
            "Return Markdown report and JSON:\n"
            '{"action_items": [{"id": "ACT-001", "title": "...", '
            '"description": "...", "priority": "...", "category": "...", '
            '"owner": "...", "finding": "..."}]}\n\n'
            f"## Source Document\n{source[:6000]}\n"
        )
        if prior_text:
            prompt += f"\n## Prior Outputs\n{prior_text[:4000]}\n"

        req = InferenceRequest(
            prompt=prompt,
            task_type=self.config.get("model", "reasoning"),
            metadata={"agent": "ActionItemAgent"},
        )
        resp = llm_invoke(self.config, req)
        output = resp.output.strip()

        self.publish_event({"type": "AgentCompleted", "agent": "ActionItemAgent"})
        return {"agent": "ActionItemAgent", "output": output}
