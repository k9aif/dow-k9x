from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Any, Callable, Dict, Optional

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

_SE_AGENTS = {
    "CriteriaLoaderAgent": CriteriaLoaderAgent,
    "EvidenceCollectorAgent": EvidenceCollectorAgent,
    "ReadinessScorerAgent": ReadinessScorerAgent,
    "GapReporterAgent": GapReporterAgent,
    "ArtifactFetcherAgent": ArtifactFetcherAgent,
    "CompletenessCheckerAgent": CompletenessCheckerAgent,
    "PackageBuilderAgent": PackageBuilderAgent,
}

SE_REVIEWS = ["SE-REVIEW-SRR", "SE-REVIEW-SFR", "SE-REVIEW-PDR", "SE-REVIEW-CDR", "SE-REVIEW-TRR"]


class SeOrchestrator(BaseOrchestrator):
    """SE Orchestrator — technical baseline and design reviews.

    Owns: Gate Readiness Squad, Package Assembly Squad.
    Runs INSIDE the acquisition pathway — activates after the iterative
    requirements/funding loop stabilizes (SWP cut).
    Gates: SRR, SFR, PDR, CDR, TRR (all non-delegable).

    Starts when DasRouter routes a ``gate_approved`` PATHWAY-MILESTONE event
    here (the human decision made in K9X HIL). In the reference deployment
    the SE stage is a **demonstration endpoint** (``se.demo_stub``, default
    true): it records that SE has been triggered and which review is next
    (SRR), and ends the pipeline without running the review squads. Set
    ``se.demo_stub: false`` to run the Gate Readiness / Package Assembly
    squads for the target review.
    """

    layer = "DAS SE Orchestrator"

    def __init__(self, config: Optional[Dict[str, Any]] = None,
                 progress_callback: Optional[Callable[[dict], None]] = None, **kwargs) -> None:
        super().__init__(config=config or {}, **kwargs)
        self._squads_dir = Path(__file__).resolve().parent.parent / "squads" / "yaml"
        self._agents_dir = Path(__file__).resolve().parent.parent / "agents" / "yaml"
        self._progress = progress_callback or (lambda e: None)
        self._demo_stub = bool((self.config.get("se") or {}).get("demo_stub", True))

    def _emit(self, event_type: str, **kwargs):
        self._progress({"type": event_type, "orchestrator": "SeOrchestrator", **kwargs})

    def _load_squad(self, yaml_filename: str, squad_id: str):
        agent_loader = AgentLoader(self._agents_dir)
        registry = AgentRegistry()
        for name, cls in _SE_AGENTS.items():
            registry.register(
                name,
                lambda c=cls, n=name: c(config=agent_loader.merge_with_global(n, self.config)),
            )
        loader = SquadLoader(registry)
        return loader.load_one(str(self._squads_dir / yaml_filename), squad_id)

    def execute_flow(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        job_id = payload.get("job_id", "unknown")
        target_review = payload.get("target_review", "SE-REVIEW-SRR")
        decision = payload.get("decision") or {}
        log.info("[SE] Starting review %s for job=%s", target_review, job_id)
        t0 = time.monotonic()
        self._emit("OrchestratorStarted", job_id=job_id, after_gate="PATHWAY-MILESTONE",
                   approved_by=decision.get("actor"), target_review=target_review)

        if self._demo_stub:
            note = (f"Systems Engineering triggered by the PATHWAY-MILESTONE approval. "
                    f"Next review: {target_review}. SE review squads are not executed in "
                    f"the reference deployment (demonstration endpoint).")
            print(f"  ✓ SE stage reached for job={job_id} (demonstration endpoint, next review {target_review})",
                  flush=True)
            self._emit("OrchestratorCompleted", job_id=job_id, elapsed_s=round(time.monotonic() - t0, 1),
                       gate=target_review, demo_stub=True)
            return {
                "job_id": job_id,
                "orchestrator": "se",
                "status": "pipeline_complete",
                "demo_stub": True,
                "target_review": target_review,
                "milestone_decision": decision,
                "note": note,
            }

        gate_squad = self._load_squad("gate_readiness_squad.yaml", "GateReadinessSquad")
        package_squad = self._load_squad("package_assembly_squad.yaml", "PackageAssemblySquad")

        gate_payload = {**payload, "gate_id": target_review}
        gate_result = gate_squad.execute(gate_payload)
        log.info("[SE] Gate readiness scored for %s", target_review)

        package_payload = {**payload, "prior_outputs": gate_result, "gate_id": target_review}
        package_result = package_squad.execute(package_payload)
        log.info("[SE] Package assembled for %s", target_review)

        return {
            "job_id": job_id,
            "orchestrator": "se",
            "target_review": target_review,
            "status": "awaiting_gate",
            "gate_id": target_review,
            "gate_readiness": gate_result,
            "review_package": package_result,
        }
