from __future__ import annotations

from k9_aif_abb.k9_core.agent.base_agent import BaseAgent
from k9_aif_abb.k9_inference.models.inference_request import InferenceRequest
from k9_aif_abb.k9_utils.llm_invoke import llm_invoke


class LinkValidatorAgent(BaseAgent):
    """Validates proposed trace links for correctness and completeness.
    Reasons over graph shape, not free text — assertions are deterministic
    and re-checkable."""

    layer = "DAS LinkValidator"

    def __init__(self, config=None, monitor=None, **kwargs):
        super().__init__(config or {}, monitor=monitor, **kwargs)

    def execute(self, payload: dict) -> dict:
        proposed_links = payload.get("prior_outputs", {}).get("proposed_links", "")

        req = InferenceRequest(
            prompt=(
                f"Role: {self.config.get('role', 'Trace Link Validator')}\n"
                f"Goal: {self.config.get('goal', 'Validate proposed trace links')}\n\n"
                f"Instructions: {self.config.get('instructions', '')}\n\n"
                f"Proposed links:\n{proposed_links}\n\n"
                "For each proposed link, verify:\n"
                "1. The FROM entity exists and is not superseded\n"
                "2. The TO entity exists and is not superseded\n"
                "3. The relationship type is valid per the traceability model\n"
                "4. The link does not create a circular dependency\n"
                "5. Evidence supports the link assertion\n\n"
                "Output: VALID/INVALID for each link with rationale."
            ),
            metadata={"agent": self.layer},
            task_type=self.config.get("model", "reasoning"),
        )
        resp = llm_invoke(self.config, req)
        self.publish_event({"type": "AgentCompleted", "agent": self.layer})
        return {"agent": self.layer, "output": resp.output}
