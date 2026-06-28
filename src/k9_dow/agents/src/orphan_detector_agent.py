from __future__ import annotations

from k9_aif_abb.k9_core.agent.base_agent import BaseAgent
from k9_aif_abb.k9_inference.models.inference_request import InferenceRequest
from k9_aif_abb.k9_utils.llm_invoke import llm_invoke


class OrphanDetectorAgent(BaseAgent):
    """Detects orphan entities in the traceability graph: rootless requirements,
    unlinked views, disconnected test cases."""

    layer = "DAS OrphanDetector"

    def __init__(self, config=None, monitor=None, **kwargs):
        super().__init__(config or {}, monitor=monitor, **kwargs)

    def execute(self, payload: dict) -> dict:
        graph_state = payload.get("prior_outputs", {})

        req = InferenceRequest(
            prompt=(
                f"Role: {self.config.get('role', 'Traceability Orphan Detector')}\n"
                f"Goal: {self.config.get('goal', 'Find orphan entities in the trace graph')}\n\n"
                f"Instructions: {self.config.get('instructions', '')}\n\n"
                f"Current graph state:\n{graph_state}\n\n"
                "Check for:\n"
                "1. Requirements with no upward trace to a capability need (rootless)\n"
                "2. DoDAF views not linked to any live requirement (orphan views)\n"
                "3. Test cases not linked to any requirement\n"
                "4. Capability docs with no derived requirements\n\n"
                "Output each orphan with its ID, type, and recommended action."
            ),
            metadata={"agent": self.layer},
            task_type=self.config.get("model", "extraction"),
        )
        resp = llm_invoke(self.config, req)
        self.publish_event({"type": "AgentCompleted", "agent": self.layer})
        return {"agent": self.layer, "output": resp.output}
