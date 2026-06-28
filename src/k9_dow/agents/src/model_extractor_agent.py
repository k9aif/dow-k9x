from __future__ import annotations

from k9_aif_abb.k9_core.agent.base_agent import BaseAgent
from k9_aif_abb.k9_inference.models.inference_request import InferenceRequest
from k9_aif_abb.k9_utils.llm_invoke import llm_invoke


class ModelExtractorAgent(BaseAgent):
    """Extracts structured model elements from MBSE/SysML sources (via Cameo
    connector) and maps them to the traceability graph entities."""

    layer = "DAS ModelExtractor"

    def __init__(self, config=None, monitor=None, **kwargs):
        super().__init__(config or {}, monitor=monitor, **kwargs)

    def execute(self, payload: dict) -> dict:
        source = payload.get("source_markdown", "")
        prior = payload.get("prior_outputs", {})

        req = InferenceRequest(
            prompt=(
                f"Role: {self.config.get('role', 'Architecture Model Extractor')}\n"
                f"Goal: {self.config.get('goal', 'Extract model elements for graph seeding')}\n\n"
                f"Instructions: {self.config.get('instructions', '')}\n\n"
                f"Source:\n{source}\n\n"
                f"Prior outputs:\n{prior}\n\n"
                "Extract structured entities for the traceability graph:\n"
                "- CapabilityNeed nodes (id, title, description)\n"
                "- SERequirement nodes (id, shall_text, type, verification_method)\n"
                "- TechnicalBaselineItem nodes (id, name, subsystem)\n"
                "- Relationships between them\n\n"
                "Use only information present in source. Output as structured JSON."
            ),
            metadata={"agent": self.layer},
            task_type=self.config.get("model", "extraction"),
        )
        resp = llm_invoke(self.config, req)
        self.publish_event({"type": "AgentCompleted", "agent": self.layer})
        return {"agent": self.layer, "output": resp.output}
