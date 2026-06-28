from __future__ import annotations

from k9_aif_abb.k9_core.agent.base_agent import BaseAgent
from k9_aif_abb.k9_inference.models.inference_request import InferenceRequest
from k9_aif_abb.k9_utils.llm_invoke import llm_invoke


class ViewConsistencyCheckerAgent(BaseAgent):
    """Checks cross-view consistency across DoDAF views. Flags incoherence
    between OV, SV, CV families — e.g. an OV-1 operational node not
    reflected in the SV-1 system view."""

    layer = "DAS ViewConsistencyChecker"

    def __init__(self, config=None, monitor=None, **kwargs):
        super().__init__(config or {}, monitor=monitor, **kwargs)

    def execute(self, payload: dict) -> dict:
        prior = payload.get("prior_outputs", {})

        req = InferenceRequest(
            prompt=(
                f"Role: {self.config.get('role', 'DoDAF View Consistency Analyst')}\n"
                f"Goal: {self.config.get('goal', 'Check cross-view consistency')}\n\n"
                f"Instructions: {self.config.get('instructions', '')}\n\n"
                f"Generated views:\n{prior}\n\n"
                "Check for incoherence across view families:\n"
                "1. Entities in OV views must appear in corresponding SV views\n"
                "2. Capabilities in CV views must trace to operational activities\n"
                "3. System interfaces must be consistent across SV-1 and SvcV-1\n"
                "4. Standards in TV-1 must apply to referenced systems\n\n"
                "Output each incoherence as: VIEW_A <-> VIEW_B: description + severity."
            ),
            metadata={"agent": self.layer},
            task_type=self.config.get("model", "reasoning"),
        )
        resp = llm_invoke(self.config, req)
        self.publish_event({"type": "AgentCompleted", "agent": self.layer})
        return {"agent": self.layer, "output": resp.output}
