# SPDX-License-Identifier: Apache-2.0
# K9-AIF Framework
from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from k9_aif_abb.k9_core.router.base_router import BaseRouter

log = logging.getLogger(__name__)

# One topic per run of the process model (config/process_model.yaml), plus side checks.
from k9_dow.config.instance import topic as _topic

DAS_TOPICS = {k: _topic(v) for k, v in {
    "requirement": "das.requirement",
    "mdd_package": "das.mdd",
    "msa": "das.msa",
    "tmrr": "das.tmrr",
    "traceability": "das.traceability",
    "drift": "das.drift",
    "results": "das.results",
}.items()}


class DasRouter(BaseRouter):
    """DAS Router: single entry point for the Defense Acquisition System flow.

    A submitted requirement document goes to the requirement run. A recorded human approval
    (``gate_approved``) goes to the run the process model says that gate's approval starts;
    a gate that starts nothing (JCI-REVIEW, the final SE-REVIEW-SRR) goes to results. The
    Router decides where an event goes; it does not coordinate the flow.
    """

    layer = "DAS Router"

    def __init__(self, config: Optional[Dict[str, Any]] = None, **kwargs) -> None:
        super().__init__(config=config or {}, **kwargs)

    def route(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        from k9_dow.gates.hil_gateway import GATE_NEXT_STAGE

        event_type = payload.get("event_type", "")
        document_type = payload.get("document_type", "")

        if event_type == "gate_approved":
            gate_id = payload.get("gate_id", "")
            nxt = GATE_NEXT_STAGE.get(gate_id)
            if nxt:
                route_to, classification = DAS_TOPICS[nxt], f"{nxt}_run"
            elif gate_id == "SE-REVIEW-SRR":
                route_to, classification = DAS_TOPICS["results"], "pipeline_complete"
            else:
                route_to, classification = DAS_TOPICS["results"], "decision_recorded"
        elif event_type == "traceability_check":
            route_to, classification = DAS_TOPICS["traceability"], "traceability"
        elif event_type == "drift_check":
            route_to, classification = DAS_TOPICS["drift"], "drift_detection"
        else:
            # capability_gap and every document type: the Service capability requirement
            route_to, classification = DAS_TOPICS["requirement"], "requirement_run"

        log.info("[DasRouter] Routed event_type=%s doc_type=%s → %s (%s)",
                 event_type, document_type, route_to, classification)
        return {"route_to": route_to, "classification": classification, "event_type": event_type}
