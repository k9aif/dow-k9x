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

        # Prior-stage results arrive as agent records ({"agent", "output", ...})
        # or plain text; count either when it carries real content.
        artifacts = {}
        for key, value in prior.items():
            text = value.get("output") if isinstance(value, dict) else value
            if isinstance(text, str) and len(text) > 50:
                artifacts[key] = {"content_length": len(text), "available": True,
                                  "agent": value.get("agent") if isinstance(value, dict) else None}

        self.publish_event({"type": "AgentCompleted", "agent": self.layer})
        return {
            "agent": self.layer,
            "gate_id": gate_id,
            "artifacts_found": len(artifacts),
            "manifest": artifacts,
            "output": f"Fetched {len(artifacts)} artifacts for gate {gate_id}",
        }
