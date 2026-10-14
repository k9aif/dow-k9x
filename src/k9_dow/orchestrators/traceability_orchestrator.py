from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, Optional

from k9_aif_abb.k9_core.orchestration.base_orchestrator import BaseOrchestrator

log = logging.getLogger(__name__)


class TraceabilityOrchestrator(BaseOrchestrator):
    """Cross-cutting orchestrator for Traceability + Drift Detection.

    Owns two squads that run in parallel. Consumes from das.traceability
    and das.drift topics. Can also be triggered on-demand after any
    orchestrator completes a stage.
    """

    layer = "DAS Traceability Orchestrator"

    def __init__(self, config: Optional[Dict[str, Any]] = None, squads=None, **kwargs) -> None:
        config = config or {}
        if "governance" not in kwargs and ((config.get("security") or {}).get("shield") or {}).get("enabled") is True:
            from k9_aif_abb.k9_security.vulnerability.shield_governance import ShieldGovernance
            kwargs["governance"] = ShieldGovernance(config)
        super().__init__(config=config, **kwargs)
        if squads is None:
            from k9_dow.squads.das_squad import squad_layer
            squads = squad_layer(config)
        self.squads = squads          # the squad layer: squads by YAML file and id, never agents
        self._squads_dir = Path(__file__).resolve().parent.parent / "squads" / "yaml"

    def _load_squad(self, yaml_filename: str, squad_id: str):
        return self.squads.load_one(self._squads_dir / yaml_filename, squad_id)

    def execute_flow(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        job_id = payload.get("job_id", "unknown")
        log.info("[Traceability] Starting cross-cutting analysis for job=%s", job_id)
        sh = self.apply_shield(payload)
        if not sh["allowed"]:
            return {"job_id": job_id, "orchestrator": "traceability", "status": "denied", "reason": sh["reason"]}
        payload = sh["payload"]

        traceability_squad = self._load_squad("traceability_squad.yaml", "TraceabilitySquad")
        drift_squad = self._load_squad("drift_detection_squad.yaml", "DriftDetectionSquad")

        results = self.execute_squads(
            [traceability_squad, drift_squad], payload, parallel=True,
        )

        log.info("[Traceability] Cross-cutting analysis complete for job=%s", job_id)

        return {
            "job_id": job_id,
            "orchestrator": "traceability",
            "status": "completed",
            **results,
        }
