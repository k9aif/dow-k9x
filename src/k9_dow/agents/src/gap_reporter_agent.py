from __future__ import annotations

from k9_aif_abb.k9_core.agent.base_agent import BaseAgent
from k9_aif_abb.k9_inference.models.inference_request import InferenceRequest
from k9_aif_abb.k9_utils.llm_invoke import llm_invoke
from k9_dow.agents.src.process_facts import PROCESS_FACTS
from k9_dow.agents.src.squad_context import gate_criteria, step_output
from k9_dow.gates.readiness import align_score, computed_score


class GapReporterAgent(BaseAgent):
    """Reports gaps identified during gate readiness assessment. Produces
    actionable gap list with remediation recommendations."""

    layer = "DAS GapReporter"

    def __init__(self, config=None, monitor=None, **kwargs):
        super().__init__(config or {}, monitor=monitor, **kwargs)

    def execute(self, payload: dict) -> dict:

        req = InferenceRequest(
            prompt=(
                f"Role: {self.config.get('role', 'Gate Gap Reporter')}\n"
                f"Goal: {self.config.get('goal', 'Report gaps blocking gate readiness')}\n\n"
                f"Instructions: {self.config.get('instructions', '')}\n\n"
                + PROCESS_FACTS + "\n" +
                f"Entry criteria: {gate_criteria(payload)}\n\n"
                f"Readiness assessment (from the Readiness Scorer):\n{step_output(payload, 'readiness_score')}\n\n"
                "For each NOT_MET or PARTIALLY_MET criterion:\n"
                "1. Describe the gap precisely\n"
                "2. Impact on proceeding (blocker vs risk-acceptance)\n"
                "3. Recommended remediation action\n"
                "4. Estimated effort to close the gap\n\n"
                "State the Overall Readiness Score exactly as the assessment gives it; never\n"
                "recompute or restate a different score.\n"
                "Output as structured gap report for decision authority."
            ),
            metadata={"agent": self.layer},
            task_type=self.config.get("model", "reasoning"),
        )
        resp = llm_invoke(self.config, req)
        self.publish_event({"type": "AgentCompleted", "agent": self.layer})
        return {"agent": self.layer, "output": align_score(resp.output or "", computed_score(payload))}
