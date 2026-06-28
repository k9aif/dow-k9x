from __future__ import annotations

from k9_aif_abb.k9_core.agent.base_agent import BaseAgent
from k9_aif_abb.k9_inference.models.inference_request import InferenceRequest
from k9_aif_abb.k9_utils.llm_invoke import llm_invoke


class BaselineDifferAgent(BaseAgent):
    """Diffs the current JCIDS requirements against the SE technical baseline
    to detect divergence. Flags when requirements have changed but the
    baseline hasn't been updated."""

    layer = "DAS BaselineDiffer"

    def __init__(self, config=None, monitor=None, **kwargs):
        super().__init__(config or {}, monitor=monitor, **kwargs)

    def execute(self, payload: dict) -> dict:
        prior = payload.get("prior_outputs", {})

        req = InferenceRequest(
            prompt=(
                f"Role: {self.config.get('role', 'Baseline Drift Analyst')}\n"
                f"Goal: {self.config.get('goal', 'Detect drift between requirements and SE baseline')}\n\n"
                f"Instructions: {self.config.get('instructions', '')}\n\n"
                f"Current state:\n{prior}\n\n"
                "Compare JCIDS requirements state against SEP baseline:\n"
                "1. Requirements added since last baseline\n"
                "2. Requirements modified but baseline not updated\n"
                "3. Requirements superseded but still referenced in baseline\n"
                "4. Baseline items with no corresponding live requirement\n\n"
                "Output each drift as: ENTITY_ID, drift_type, description, severity."
            ),
            metadata={"agent": self.layer},
            task_type=self.config.get("model", "reasoning"),
        )
        resp = llm_invoke(self.config, req)
        self.publish_event({"type": "AgentCompleted", "agent": self.layer})
        return {"agent": self.layer, "output": resp.output}
