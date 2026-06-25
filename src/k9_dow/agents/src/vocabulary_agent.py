# SPDX-License-Identifier: Apache-2.0
# DoW Architecture Workbench — VocabularyAgent (SBB)

from typing import Any, Dict, Optional

from k9_aif_abb.k9_core.agent.base_agent import BaseAgent
from k9_aif_abb.k9_inference.models.inference_request import InferenceRequest
from k9_aif_abb.k9_utils.llm_invoke import llm_invoke


class VocabularyAgent(BaseAgent):
    layer = "DoW Vocabulary SBB"

    def __init__(self, config: Optional[Dict[str, Any]] = None, monitor=None, **kwargs):
        super().__init__(config or {}, monitor=monitor, **kwargs)

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        source = payload.get("source_markdown") or ""
        prior = payload.get("prior_outputs") or {}
        prior_text = "\n".join(prior.values()) if prior else ""

        prompt = (
            f"Role: {self.config.get('role', 'Architecture Vocabulary and Terminology Analyst')}\n"
            f"Goal: {self.config.get('goal', 'Build an AV-2 Integrated Dictionary vocabulary seed')}\n\n"
            "## Grounding Rules\n"
            "Use only the source document and approved prior-stage outputs.\n"
            "Do not invent facts. If evidence is missing, write: NOT PROVIDED IN SOURCE.\n"
            "Include short source evidence snippets. Keep tone neutral, government-review-ready.\n\n"
            "## Task\n"
            "Build an AV-2 Integrated Dictionary vocabulary seed from the source document.\n"
            "Extract all significant domain terms, acronyms, and definitions.\n"
            "For each entry provide:\n"
            "- Term\n"
            "- Definition (as stated in source, or inferred from context)\n"
            "- Category (acronym/concept/system/organization/standard/process)\n"
            "- Source reference (section or paragraph where term appears)\n\n"
            "Group terms alphabetically.\n\n"
            "If no significant terminology found, write: NOT PROVIDED IN SOURCE\n\n"
            "Return Markdown report and JSON:\n"
            '{"vocabulary": [{"term": "...", "definition": "...", "category": "...", '
            '"source_reference": "..."}]}\n\n'
            f"## Source Document\n{source[:6000]}\n"
        )
        if prior_text:
            prompt += f"\n## Prior Outputs\n{prior_text[:4000]}\n"

        req = InferenceRequest(
            prompt=prompt,
            task_type=self.config.get("model", "reasoning"),
            metadata={"agent": "VocabularyAgent"},
        )
        resp = llm_invoke(self.config, req)
        output = resp.output.strip()

        self.publish_event({"type": "AgentCompleted", "agent": "VocabularyAgent"})
        return {"agent": "VocabularyAgent", "output": output}
