from __future__ import annotations

from k9_aif_abb.k9_core.agent.base_agent import BaseAgent
from k9_aif_abb.k9_inference.models.inference_request import InferenceRequest
from k9_aif_abb.k9_utils.llm_invoke import llm_invoke
from datetime import date

from k9_dow.agents.src.squad_context import gate_criteria, step_output
from k9_dow.gates.readiness import apply_computed_score


class ReadinessScorerAgent(BaseAgent):
    """Scores gate readiness based on evidence vs criteria. Agents score;
    humans decide. The score informs the decision authority — it does not
    replace them."""

    layer = "DAS ReadinessScorer"

    def __init__(self, config=None, monitor=None, **kwargs):
        super().__init__(config or {}, monitor=monitor, **kwargs)

    def execute(self, payload: dict) -> dict:
        gate_id = payload.get("gate_id", "")
        criteria = gate_criteria(payload)
        today = date.today().isoformat()

        req = InferenceRequest(
            prompt=(
                f"Role: {self.config.get('role', 'Gate Readiness Scorer')}\n"
                f"Goal: {self.config.get('goal', 'Score readiness against gate criteria')}\n\n"
                f"Instructions: {self.config.get('instructions', '')}\n\n"
                f"Gate: {gate_id}\n"
                f"Assessment date: {today}\n"
                f"Entry criteria: {criteria}\n\n"
                f"Evidence mapping (from the Evidence Collector):\n{step_output(payload, 'evidence')}\n\n"
                "For each criterion, in the order given, state its verdict: MET / PARTIALLY_MET / NOT_MET,\n"
                "with rationale and evidence reference. Name each criterion exactly as written above.\n"
                "Do NOT compute or state an overall score: it is computed from your verdicts and the\n"
                "gate's criterion weights.\n"
                "Flag any criterion that blocks proceeding.\n"
                "Output: structured readiness assessment for human decision authority."
            ),
            metadata={"agent": self.layer},
            task_type=self.config.get("model", "reasoning"),
        )
        resp = llm_invoke(self.config, req)
        scored = apply_computed_score(resp.output or "", gate_id, criteria, today)
        self.publish_event({"type": "AgentCompleted", "agent": self.layer, "score": scored["score"]})
        return {"agent": self.layer, **scored}
