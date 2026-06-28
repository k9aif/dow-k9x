from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, Optional

from k9_aif_abb.k9_agents.registry.agent_registry import AgentRegistry
from k9_aif_abb.k9_core.orchestration.base_orchestrator import BaseOrchestrator
from k9_aif_abb.k9_squad.squad_loader import SquadLoader

from k9_dow.utils.agent_loader import AgentLoader
from k9_dow.agents.src.link_proposer_agent import LinkProposerAgent
from k9_dow.agents.src.link_validator_agent import LinkValidatorAgent
from k9_dow.agents.src.orphan_detector_agent import OrphanDetectorAgent
from k9_dow.agents.src.coverage_scorer_agent import CoverageScorerAgent
from k9_dow.agents.src.baseline_differ_agent import BaselineDifferAgent
from k9_dow.agents.src.funding_differ_agent import FundingDifferAgent
from k9_dow.agents.src.drift_classifier_agent import DriftClassifierAgent

log = logging.getLogger(__name__)

_CROSS_CUTTING_AGENTS = {
    "LinkProposerAgent": LinkProposerAgent,
    "LinkValidatorAgent": LinkValidatorAgent,
    "OrphanDetectorAgent": OrphanDetectorAgent,
    "CoverageScorerAgent": CoverageScorerAgent,
    "BaselineDifferAgent": BaselineDifferAgent,
    "FundingDifferAgent": FundingDifferAgent,
    "DriftClassifierAgent": DriftClassifierAgent,
}


class TraceabilityOrchestrator(BaseOrchestrator):
    """Cross-cutting orchestrator for Traceability + Drift Detection.

    Owns two squads that run in parallel. Consumes from das.traceability
    and das.drift topics. Can also be triggered on-demand after any
    orchestrator completes a stage.
    """

    layer = "DAS Traceability Orchestrator"

    def __init__(self, config: Optional[Dict[str, Any]] = None, **kwargs) -> None:
        super().__init__(config=config or {}, **kwargs)
        self._squads_dir = Path(__file__).resolve().parent.parent / "squads" / "yaml"
        self._agents_dir = Path(__file__).resolve().parent.parent / "agents" / "yaml"

    def _load_squad(self, yaml_filename: str, squad_id: str):
        agent_loader = AgentLoader(self._agents_dir)
        registry = AgentRegistry()
        for name, cls in _CROSS_CUTTING_AGENTS.items():
            registry.register(
                name,
                lambda c=cls, n=name: c(config=agent_loader.merge_with_global(n, self.config)),
            )
        loader = SquadLoader(registry)
        return loader.load_one(str(self._squads_dir / yaml_filename), squad_id)

    def execute_flow(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        job_id = payload.get("job_id", "unknown")
        log.info("[Traceability] Starting cross-cutting analysis for job=%s", job_id)

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
