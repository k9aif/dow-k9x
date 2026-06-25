# SPDX-License-Identifier: Apache-2.0
# DoW Architecture Workbench — SystemServiceExtractorAgent (SBB)

from typing import Any, Dict, Optional

from k9_aif_abb.k9_core.agent.base_agent import BaseAgent
from k9_aif_abb.k9_inference.models.inference_request import InferenceRequest
from k9_aif_abb.k9_utils.llm_invoke import llm_invoke


class SystemServiceExtractorAgent(BaseAgent):
    layer = "DoW SystemServiceExtractor SBB"

    def __init__(self, config: Optional[Dict[str, Any]] = None, monitor=None, **kwargs):
        super().__init__(config or {}, monitor=monitor, **kwargs)

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        source = payload.get("source_markdown") or ""
        prior = payload.get("prior_outputs") or {}
        prior_text = "\n".join(prior.values()) if prior else ""

        prompt = (
            f"Role: {self.config.get('role', 'Systems and Services Analyst')}\n"
            f"Goal: {self.config.get('goal', 'Extract systems, services, and their interfaces')}\n\n"
            "## Grounding Rules\n"
            "Use only the source document and approved prior-stage outputs.\n"
            "Do not invent facts. If evidence is missing, write: NOT PROVIDED IN SOURCE.\n"
            "Include short source evidence snippets. Keep tone neutral, government-review-ready.\n\n"
            "## Task\n"
            "Extract all systems, services, and their interfaces from the source.\n"
            "For each system or service provide:\n"
            "- Name\n"
            "- Type (system/service/platform/application)\n"
            "- Description\n"
            "- Hosting system (if applicable)\n"
            "- Interfaces and dependencies\n"
            "- DoDAF mapping (SV-1 for systems, SvcV-1 for services)\n"
            "- Verbatim evidence from the source\n\n"
            "If not found: NOT PROVIDED IN SOURCE\n\n"
            "Return Markdown report and JSON:\n"
            '{"systems": [{"name": "...", "type": "...", "description": "...", '
            '"hosting": "...", "interfaces": ["..."], "dodaf_view": "...", "evidence": "..."}], '
            '"services": [{"name": "...", "type": "...", "description": "...", '
            '"provider": "...", "consumers": ["..."], "dodaf_view": "...", "evidence": "..."}]}\n\n'
            f"## Source Document\n{source[:6000]}\n"
        )
        if prior_text:
            prompt += f"\n## Prior Outputs\n{prior_text[:4000]}\n"

        req = InferenceRequest(
            prompt=prompt,
            task_type=self.config.get("model", "reasoning"),
            metadata={"agent": "SystemServiceExtractorAgent"},
        )
        resp = llm_invoke(self.config, req)
        output = resp.output.strip()

        self.publish_event({"type": "AgentCompleted", "agent": "SystemServiceExtractorAgent"})
        return {"agent": "SystemServiceExtractorAgent", "output": output}
