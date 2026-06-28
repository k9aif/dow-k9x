from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from k9_aif_abb.k9_core.router.base_router import BaseRouter

log = logging.getLogger(__name__)

DAS_TOPICS = {
    "jcids": "das.jcids",
    "acquisition": "das.acquisition",
    "se": "das.se",
    "traceability": "das.traceability",
    "drift": "das.drift",
    "results": "das.results",
}


class DasRouter(BaseRouter):
    """DAS Router — single entry point for the Defense Acquisition System pipeline.

    Routes capability gap documents to the appropriate orchestrator topic.
    The cascade (JCIDS → Acquisition → SE) happens via Kafka topic chaining
    after HITL gates resolve — the Router makes the initial routing decision,
    it does not coordinate the flow.
    """

    layer = "DAS Router"

    def __init__(self, config: Optional[Dict[str, Any]] = None, **kwargs) -> None:
        super().__init__(config=config or {}, **kwargs)

    def route(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        event_type = payload.get("event_type", "")
        document_type = payload.get("document_type", "")

        if event_type == "capability_gap" or document_type in (
            "capability_gap", "capability_needs", "conops", "architecture_document",
        ):
            route_to = DAS_TOPICS["jcids"]
            classification = "jcids_pipeline"

        elif event_type == "gate_approved":
            gate_id = payload.get("gate_id", "")
            if gate_id == "JROC-VALIDATION":
                route_to = DAS_TOPICS["acquisition"]
                classification = "acquisition_pipeline"
            elif gate_id == "PATHWAY-MILESTONE":
                route_to = DAS_TOPICS["se"]
                classification = "se_pipeline"
            elif gate_id.startswith("SE-REVIEW-"):
                route_to = DAS_TOPICS["results"]
                classification = "pipeline_complete"
            else:
                route_to = DAS_TOPICS["results"]
                classification = "unknown_gate"

        elif event_type == "traceability_check":
            route_to = DAS_TOPICS["traceability"]
            classification = "traceability"

        elif event_type == "drift_check":
            route_to = DAS_TOPICS["drift"]
            classification = "drift_detection"

        else:
            route_to = DAS_TOPICS["jcids"]
            classification = "default_to_jcids"

        log.info(
            "[DasRouter] Routed event_type=%s doc_type=%s → %s (%s)",
            event_type, document_type, route_to, classification,
        )

        return {
            "route_to": route_to,
            "classification": classification,
            "event_type": event_type,
        }
