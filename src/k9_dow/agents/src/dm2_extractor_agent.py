# SPDX-License-Identifier: Apache-2.0
# DoW Architecture Workbench — DM2ExtractorAgent (SBB)

from typing import Any, Dict, Optional

from k9_aif_abb.k9_core.agent.base_agent import BaseAgent
from k9_aif_abb.k9_inference.models.inference_request import InferenceRequest
from k9_aif_abb.k9_utils.llm_invoke import llm_invoke


class DM2ExtractorAgent(BaseAgent):
    layer = "DoW DM2Extractor SBB"

    def __init__(self, config: Optional[Dict[str, Any]] = None, monitor=None, **kwargs):
        super().__init__(config or {}, monitor=monitor, **kwargs)

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        source = payload.get("source_markdown") or ""
        prior = payload.get("prior_outputs") or {}
        prior_text = "\n".join(prior.values()) if prior else ""

        prompt = (
            f"Role: {self.config.get('role', 'DoDAF Meta-Model (DM2) Data Modeler')}\n"
            f"Goal: {self.config.get('goal', 'Extract DM2 entities and relationships from all available data')}\n\n"
            "## Grounding Rules\n"
            "Use only the source document and approved prior-stage outputs.\n"
            "Do not invent facts. If evidence is missing, write: NOT PROVIDED IN SOURCE.\n"
            "Include short source evidence snippets. Keep tone neutral, government-review-ready.\n\n"
            "## Task\n"
            "Extract DM2 entities and relationships from all available data.\n\n"
            "DM2 entity types to identify:\n"
            "- Performer (organizations, roles, systems)\n"
            "- Activity (operational activities, functions)\n"
            "- Resource (information, data, materiel)\n"
            "- Service (provided services, service descriptions)\n"
            "- Capability (mission capabilities)\n"
            "- Measure (metrics, KPIs)\n"
            "- Location (geographic, logical)\n"
            "- Condition (rules, constraints, standards)\n\n"
            "For each entity provide:\n"
            "- Entity name\n"
            "- DM2 type\n"
            "- Description\n"
            "- Verbatim evidence\n\n"
            "For relationships provide:\n"
            "- Source entity\n"
            "- Relationship type (performs, produces, consumes, supports, etc.)\n"
            "- Target entity\n\n"
            "If not found: NOT PROVIDED IN SOURCE\n\n"
            "Return Markdown report and JSON:\n"
            '{"entities": [{"name": "...", "dm2_type": "...", "description": "...", "evidence": "..."}], '
            '"relationships": [{"source": "...", "relationship": "...", "target": "..."}]}\n\n'
            f"## Source Document\n{source[:6000]}\n"
        )
        if prior_text:
            prompt += f"\n## Prior Outputs\n{prior_text[:4000]}\n"

        req = InferenceRequest(
            prompt=prompt,
            task_type=self.config.get("model", "reasoning"),
            metadata={"agent": "DM2ExtractorAgent"},
        )
        resp = llm_invoke(self.config, req)
        output = resp.output.strip()

        self.publish_event({"type": "AgentCompleted", "agent": "DM2ExtractorAgent"})
        return {"agent": "DM2ExtractorAgent", "output": output}
