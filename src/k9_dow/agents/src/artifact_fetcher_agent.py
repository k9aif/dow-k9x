from __future__ import annotations

from k9_aif_abb.k9_core.agent.base_agent import BaseAgent


class ArtifactFetcherAgent(BaseAgent):
    """Fetches artifacts from connectors and prior pipeline outputs.
    Deterministic — gathers what's available, does not generate."""

    layer = "DAS ArtifactFetcher"

    def __init__(self, config=None, monitor=None, **kwargs):
        super().__init__(config or {}, monitor=monitor, **kwargs)

    def execute(self, payload: dict) -> dict:
        prior = payload.get("prior_outputs", {})
        gate_id = payload.get("gate_id", "")

        artifacts = {}
        for key, value in prior.items():
            if isinstance(value, str) and len(value) > 50:
                artifacts[key] = {"content_length": len(value), "available": True}

        self.publish_event({"type": "AgentCompleted", "agent": self.layer})
        return {
            "agent": self.layer,
            "gate_id": gate_id,
            "artifacts_found": len(artifacts),
            "manifest": artifacts,
            "output": f"Fetched {len(artifacts)} artifacts for gate {gate_id}",
        }
