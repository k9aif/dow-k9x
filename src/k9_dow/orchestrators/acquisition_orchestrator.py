from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, Optional

from k9_aif_abb.k9_agents.registry.agent_registry import AgentRegistry
from k9_aif_abb.k9_core.orchestration.base_orchestrator import BaseOrchestrator
from k9_aif_abb.k9_squad.squad_loader import SquadLoader

from k9_dow.utils.agent_loader import AgentLoader
from k9_dow.agents.src.criteria_loader_agent import CriteriaLoaderAgent
from k9_dow.agents.src.evidence_collector_agent import EvidenceCollectorAgent
from k9_dow.agents.src.readiness_scorer_agent import ReadinessScorerAgent
from k9_dow.agents.src.gap_reporter_agent import GapReporterAgent
from k9_dow.agents.src.artifact_fetcher_agent import ArtifactFetcherAgent
from k9_dow.agents.src.completeness_checker_agent import CompletenessCheckerAgent
from k9_dow.agents.src.package_builder_agent import PackageBuilderAgent

log = logging.getLogger(__name__)

_ACQ_AGENTS = {
    "CriteriaLoaderAgent": CriteriaLoaderAgent,
    "EvidenceCollectorAgent": EvidenceCollectorAgent,
    "ReadinessScorerAgent": ReadinessScorerAgent,
    "GapReporterAgent": GapReporterAgent,
    "ArtifactFetcherAgent": ArtifactFetcherAgent,
    "CompletenessCheckerAgent": CompletenessCheckerAgent,
    "PackageBuilderAgent": PackageBuilderAgent,
}


class AcquisitionOrchestrator(BaseOrchestrator):
    """Acquisition/PPBE Orchestrator — pathway selection + funding.

    Owns: Gate Readiness Squad, Package Assembly Squad.
    Gate: PATHWAY-MILESTONE (non-delegable).
    """

    layer = "DAS Acquisition Orchestrator"

    def __init__(self, config: Optional[Dict[str, Any]] = None, **kwargs) -> None:
        super().__init__(config=config or {}, **kwargs)
        self._squads_dir = Path(__file__).resolve().parent.parent / "squads" / "yaml"
        self._agents_dir = Path(__file__).resolve().parent.parent / "agents" / "yaml"

    def _load_squad(self, yaml_filename: str, squad_id: str):
        agent_loader = AgentLoader(self._agents_dir)
        registry = AgentRegistry()
        for name, cls in _ACQ_AGENTS.items():
            registry.register(
                name,
                lambda c=cls, n=name: c(config=agent_loader.merge_with_global(n, self.config)),
            )
        loader = SquadLoader(registry)
        return loader.load_one(str(self._squads_dir / yaml_filename), squad_id)

    def execute_flow(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        job_id = payload.get("job_id", "unknown")
        log.info("[Acquisition] Starting for job=%s", job_id)

        gate_squad = self._load_squad("gate_readiness_squad.yaml", "GateReadinessSquad")
        package_squad = self._load_squad("package_assembly_squad.yaml", "PackageAssemblySquad")

        results = self.execute_squads(
            [gate_squad, package_squad],
            {**payload, "gate_id": "PATHWAY-MILESTONE"},
        )

        return {
            "job_id": job_id,
            "orchestrator": "acquisition",
            "status": "awaiting_gate",
            "gate_id": "PATHWAY-MILESTONE",
            **results,
        }
