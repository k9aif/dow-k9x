from __future__ import annotations

from k9_aif_abb.k9_core.agent.base_agent import BaseAgent


class CriteriaLoaderAgent(BaseAgent):
    """Loads gate entry criteria for the target review. Deterministic —
    no LLM needed. Reads criteria from gate registry."""

    layer = "DAS CriteriaLoader"

    def __init__(self, config=None, monitor=None, **kwargs):
        super().__init__(config or {}, monitor=monitor, **kwargs)

    def execute(self, payload: dict) -> dict:
        gate_id = payload.get("gate_id", "")
        gate_criteria = payload.get("gate_criteria", [])

        self.publish_event({"type": "AgentCompleted", "agent": self.layer, "gate_id": gate_id})
        return {
            "agent": self.layer,
            "gate_id": gate_id,
            "criteria": gate_criteria,
            # The review document shows this text: the criteria themselves, not a count.
            "output": (f"Entry criteria for {gate_id} (process model):\n\n"
                       + "\n".join(f"{i}. {c}" for i, c in enumerate(gate_criteria, 1))
                       if gate_criteria else f"No entry criteria configured for {gate_id}."),
        }
