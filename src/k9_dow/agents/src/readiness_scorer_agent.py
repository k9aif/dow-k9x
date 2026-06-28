from __future__ import annotations

from k9_aif_abb.k9_core.agent.base_agent import BaseAgent
from k9_aif_abb.k9_inference.models.inference_request import InferenceRequest
from k9_aif_abb.k9_utils.llm_invoke import llm_invoke


class ReadinessScorerAgent(BaseAgent):
    """Scores gate readiness based on evidence vs criteria. Agents score;
    humans decide. The score informs the decision authority — it does not
    replace them."""

    layer = "DAS ReadinessScorer"

    def __init__(self, config=None, monitor=None, **kwargs):
        super().__init__(config or {}, monitor=monitor, **kwargs)

    def execute(self, payload: dict) -> dict:
        prior = payload.get("prior_outputs", {})
        gate_id = payload.get("gate_id", "")

        req = InferenceRequest(
            prompt=(
                f"Role: {self.config.get('role', 'Gate Readiness Scorer')}\n"
                f"Goal: {self.config.get('goal', 'Score readiness against gate criteria')}\n\n"
                f"Instructions: {self.config.get('instructions', '')}\n\n"
                f"Gate: {gate_id}\n"
                f"Evidence collected:\n{prior}\n\n"
                "For each criterion, score as: MET / PARTIALLY_MET / NOT_MET with rationale.\n"
                "Compute overall readiness score (0-100).\n"
                "Flag any criterion that blocks proceeding.\n"
                "Output: structured readiness assessment for human decision authority."
            ),
            metadata={"agent": self.layer},
            task_type=self.config.get("model", "reasoning"),
        )
        resp = llm_invoke(self.config, req)
        self.publish_event({"type": "AgentCompleted", "agent": self.layer})
        return {"agent": self.layer, "output": resp.output}
