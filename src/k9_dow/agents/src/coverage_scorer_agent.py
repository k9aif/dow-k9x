from __future__ import annotations

from k9_aif_abb.k9_core.agent.base_agent import BaseAgent
from k9_aif_abb.k9_inference.models.inference_request import InferenceRequest
from k9_aif_abb.k9_utils.llm_invoke import llm_invoke


class CoverageScorerAgent(BaseAgent):
    """Scores traceability coverage across the graph. Produces a coverage
    report showing verified vs unverified requirements, trace completeness,
    and gap analysis."""

    layer = "DAS CoverageScorer"

    def __init__(self, config=None, monitor=None, **kwargs):
        super().__init__(config or {}, monitor=monitor, **kwargs)

    def execute(self, payload: dict) -> dict:
        prior = payload.get("prior_outputs", {})

        req = InferenceRequest(
            prompt=(
                f"Role: {self.config.get('role', 'Traceability Coverage Analyst')}\n"
                f"Goal: {self.config.get('goal', 'Score traceability coverage')}\n\n"
                f"Instructions: {self.config.get('instructions', '')}\n\n"
                f"Trace analysis:\n{prior}\n\n"
                "Compute and report:\n"
                "1. Total requirements vs verified requirements (coverage %)\n"
                "2. Requirements by maturity level (identified/analyzed/allocated/verified)\n"
                "3. Invariant check results (4 invariants)\n"
                "4. Risk areas: requirements with low coverage or missing traces\n"
                "5. Overall traceability health score (0-100)\n\n"
                "Output as structured coverage report."
            ),
            metadata={"agent": self.layer},
            task_type=self.config.get("model", "reasoning"),
        )
        resp = llm_invoke(self.config, req)
        self.publish_event({"type": "AgentCompleted", "agent": self.layer})
        return {"agent": self.layer, "output": resp.output}
