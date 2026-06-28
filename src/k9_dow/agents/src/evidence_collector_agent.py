from __future__ import annotations

from k9_aif_abb.k9_core.agent.base_agent import BaseAgent
from k9_aif_abb.k9_inference.models.inference_request import InferenceRequest
from k9_aif_abb.k9_utils.llm_invoke import llm_invoke


class EvidenceCollectorAgent(BaseAgent):
    """Collects evidence artifacts that satisfy gate entry criteria.
    Assembles the evidence package that will be presented to the human
    decision authority at the HITL gate."""

    layer = "DAS EvidenceCollector"

    def __init__(self, config=None, monitor=None, **kwargs):
        super().__init__(config or {}, monitor=monitor, **kwargs)

    def execute(self, payload: dict) -> dict:
        prior = payload.get("prior_outputs", {})
        gate_id = payload.get("gate_id", "")
        criteria = prior.get("criteria", [])

        req = InferenceRequest(
            prompt=(
                f"Role: {self.config.get('role', 'Gate Evidence Collector')}\n"
                f"Goal: {self.config.get('goal', 'Collect evidence for gate entry criteria')}\n\n"
                f"Instructions: {self.config.get('instructions', '')}\n\n"
                f"Gate: {gate_id}\n"
                f"Entry criteria: {criteria}\n\n"
                f"Available artifacts:\n{prior}\n\n"
                "For each criterion, identify the evidence artifact(s) that satisfy it. "
                "If no evidence exists, mark as EVIDENCE NOT AVAILABLE. "
                "Output: criterion → evidence mapping with references."
            ),
            metadata={"agent": self.layer},
            task_type=self.config.get("model", "extraction"),
        )
        resp = llm_invoke(self.config, req)
        self.publish_event({"type": "AgentCompleted", "agent": self.layer})
        return {"agent": self.layer, "output": resp.output}
