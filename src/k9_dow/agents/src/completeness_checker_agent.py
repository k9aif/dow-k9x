from __future__ import annotations

from k9_aif_abb.k9_core.agent.base_agent import BaseAgent
from k9_aif_abb.k9_inference.models.inference_request import InferenceRequest
from k9_aif_abb.k9_utils.llm_invoke import llm_invoke


class CompletenessCheckerAgent(BaseAgent):
    """Checks artifact package completeness against gate requirements.
    Identifies missing artifacts before the package is presented to the
    human decision authority."""

    layer = "DAS CompletenessChecker"

    def __init__(self, config=None, monitor=None, **kwargs):
        super().__init__(config or {}, monitor=monitor, **kwargs)

    def execute(self, payload: dict) -> dict:
        prior = payload.get("prior_outputs", {})
        gate_id = payload.get("gate_id", "")

        req = InferenceRequest(
            prompt=(
                f"Role: {self.config.get('role', 'Package Completeness Checker')}\n"
                f"Goal: {self.config.get('goal', 'Verify artifact package completeness')}\n\n"
                f"Instructions: {self.config.get('instructions', '')}\n\n"
                f"Gate: {gate_id}\n"
                f"Available artifacts:\n{prior}\n\n"
                "Check:\n"
                "1. All required artifacts present for this gate type\n"
                "2. No placeholder or stub content in critical artifacts\n"
                "3. Provenance recorded for each artifact\n"
                "4. All cross-references resolve\n\n"
                "Output: COMPLETE / INCOMPLETE with missing items list."
            ),
            metadata={"agent": self.layer},
            task_type=self.config.get("model", "extraction"),
        )
        resp = llm_invoke(self.config, req)
        self.publish_event({"type": "AgentCompleted", "agent": self.layer})
        return {"agent": self.layer, "output": resp.output}
