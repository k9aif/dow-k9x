from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Any, Callable, Dict, Optional

from k9_aif_abb.k9_agents.registry.agent_registry import AgentRegistry
from k9_aif_abb.k9_core.orchestration.base_orchestrator import BaseOrchestrator
from k9_aif_abb.k9_squad.squad_loader import SquadLoader

from k9_dow.utils.agent_loader import AgentLoader

log = logging.getLogger(__name__)

_ACQ_AGENTS = (
    "CriteriaLoaderAgent",
    "EvidenceCollectorAgent",
    "ReadinessScorerAgent",
    "GapReporterAgent",
    "ArtifactFetcherAgent",
    "CompletenessCheckerAgent",
    "PackageBuilderAgent",
)


class AcquisitionOrchestrator(BaseOrchestrator):
    """Acquisition/PPBE Orchestrator — pathway selection + funding.

    Owns: Gate Readiness Squad, Package Assembly Squad.
    Gate: PATHWAY-MILESTONE (non-delegable).

    Starts when DasRouter routes a ``gate_approved`` JROC-VALIDATION event
    here (the human decision made in K9X HIL, see gates/hil_gateway.py).
    Input is the JCIDS stage's stored result for the same job.
    """

    layer = "DAS Acquisition Orchestrator"
    GATE_ID = "PATHWAY-MILESTONE"

    def __init__(self, config: Optional[Dict[str, Any]] = None,
                 progress_callback: Optional[Callable[[dict], None]] = None, **kwargs) -> None:
        super().__init__(config=config or {}, **kwargs)
        self._squads_dir = Path(__file__).resolve().parent.parent / "squads" / "yaml"
        self._agents_dir = Path(__file__).resolve().parent.parent / "agents" / "yaml"
        self._progress = progress_callback or (lambda e: None)

    def _emit(self, event_type: str, **kwargs):
        self._progress({"type": event_type, "orchestrator": "AcquisitionOrchestrator", **kwargs})

    def _load_squad(self, yaml_filename: str, squad_id: str):
        agent_loader = AgentLoader(self._agents_dir)
        registry = AgentRegistry()
        for name in _ACQ_AGENTS:
            cls = agent_loader.resolve_class(name)
            registry.register(
                name,
                lambda c=cls, n=name: c(config=agent_loader.merge_with_global(n, self.config)),
            )
        loader = SquadLoader(registry)
        return loader.load_one(str(self._squads_dir / yaml_filename), squad_id)

    def _run_squad(self, squad, squad_name: str, payload: dict) -> dict:
        agents = [s.get("agent", "?") for s in getattr(squad, "flow", [])]
        self._emit("SquadStarted", squad=squad_name, agents=agents, total=len(agents))
        t0 = time.monotonic()
        result = squad.execute(payload)
        self._emit("SquadCompleted", squad=squad_name, elapsed_s=round(time.monotonic() - t0, 1))
        return result

    def execute_flow(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        from k9_dow.gates.gate_registry import DAS_GATES
        from k9_dow.gates.hil_gateway import load_stage_result, publish_gate_task, save_stage_result

        job_id = payload.get("job_id", "unknown")
        decision = payload.get("decision") or {}
        log.info("[Acquisition] Starting for job=%s (JROC approved by %s)", job_id, decision.get("actor"))
        t0 = time.monotonic()
        self._emit("OrchestratorStarted", job_id=job_id, after_gate="JROC-VALIDATION",
                   approved_by=decision.get("actor"))

        jcids = load_stage_result(self.config, job_id, "jcids") or {}
        prior = {**(jcids.get("gate_readiness") or {}), **(jcids.get("review_package") or {})}
        stage_payload = {
            **payload,
            "gate_id": self.GATE_ID,
            "gate_criteria": DAS_GATES[self.GATE_ID].entry_criteria,
            "document_title": jcids.get("document_title"),
            "prior_outputs": prior,
        }

        gate_result = self._run_squad(self._load_squad("gate_readiness_squad.yaml", "GateReadinessSquad"),
                                      "GateReadinessSquad", stage_payload)
        package_result = self._run_squad(self._load_squad("package_assembly_squad.yaml", "PackageAssemblySquad"),
                                         "PackageAssemblySquad", {**stage_payload, "prior_outputs": {**prior, **gate_result}})

        result = {
            "job_id": job_id,
            "orchestrator": "acquisition",
            "status": "awaiting_gate",
            "gate_id": self.GATE_ID,
            "document_title": jcids.get("document_title"),
            "jroc_decision": decision,
            "input_found": bool(jcids),
            "gate_readiness": gate_result,
            "review_package": package_result,
        }
        self._emit("OrchestratorCompleted", job_id=job_id, elapsed_s=round(time.monotonic() - t0, 1),
                   gate=self.GATE_ID)

        uri = save_stage_result(self.config, job_id, "acquisition", result)
        readiness = gate_result.get("readiness_score", {})
        if publish_gate_task(
            self.config, self.GATE_ID, job_id,
            title=f"PATHWAY-MILESTONE review — {job_id}",
            description="DAS Acquisition stage complete (resumed after JROC approval); milestone "
                        "decision authority review requested. Approval starts Systems Engineering.",
            source_orchestrator="AcquisitionOrchestrator",
            source_topic="das.acquisition",
            payload={
                "readiness_score": readiness.get("output") if isinstance(readiness, dict) else None,
                "jroc_approved_by": decision.get("actor"),
            },
            artifacts=[uri],
        ):
            self._emit("HilTaskPublished", job_id=job_id, topic="workflow.hil.das.pathway",
                       gate_id=self.GATE_ID, artifact=uri)
        return result
