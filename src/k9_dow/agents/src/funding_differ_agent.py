from __future__ import annotations

from k9_aif_abb.k9_core.agent.base_agent import BaseAgent
from k9_aif_abb.k9_inference.models.inference_request import InferenceRequest
from k9_aif_abb.k9_utils.llm_invoke import llm_invoke


class FundingDifferAgent(BaseAgent):
    """Diffs requirements against PPBE funding lines. Detects when
    requirements exist without funding or funding references stale records."""

    layer = "DAS FundingDiffer"

    def __init__(self, config=None, monitor=None, **kwargs):
        super().__init__(config or {}, monitor=monitor, **kwargs)

    def execute(self, payload: dict) -> dict:
        prior = payload.get("prior_outputs", {})

        req = InferenceRequest(
            prompt=(
                f"Role: {self.config.get('role', 'Funding Drift Analyst')}\n"
                f"Goal: {self.config.get('goal', 'Detect drift between requirements and funding')}\n\n"
                f"Instructions: {self.config.get('instructions', '')}\n\n"
                f"Current state:\n{prior}\n\n"
                "Compare requirements against PPBE funding lines:\n"
                "1. Requirements with no FUNDED_BY link (unfunded work)\n"
                "2. Funding lines referencing superseded requirements\n"
                "3. Fiscal year mismatches\n"
                "4. Funding line status changes (current → superseded)\n\n"
                "Output each drift as: ENTITY_ID, drift_type, description, severity."
            ),
            metadata={"agent": self.layer},
            task_type=self.config.get("model", "reasoning"),
        )
        resp = llm_invoke(self.config, req)
        self.publish_event({"type": "AgentCompleted", "agent": self.layer})
        return {"agent": self.layer, "output": resp.output}
