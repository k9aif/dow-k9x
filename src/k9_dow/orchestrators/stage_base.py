# SPDX-License-Identifier: Apache-2.0
# K9-AIF Framework
"""What every DAS stage orchestrator shares (process model mca-2026-10).

A run prepares the package for one or more human gates: optional content squads
draft the documents, the GateReadiness squad judges the gate's entry criteria
(taken from config/process_model.yaml), the PackageAssembly squad assembles the
review package, the result is stored by job id, and a K9X HIL task is published
per gate. The next run starts only from a recorded human approval
(gates/hil_gateway.py, routers/das_router.py).

Agents are named, never imported: classes resolve from each agent YAML's
``class`` + ``module`` (three-layer decoupling, k9_inspect K9-DEC-001).
"""

from __future__ import annotations

import logging
import os
import re
import time
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple

from k9_aif_abb.k9_agents.registry.agent_registry import AgentRegistry
from k9_aif_abb.k9_core.orchestration.base_orchestrator import BaseOrchestrator
from k9_aif_abb.k9_squad.squad_loader import SquadLoader

from k9_dow.utils.agent_loader import AgentLoader

log = logging.getLogger(__name__)

READINESS_AGENTS = ("CriteriaLoaderAgent", "EvidenceCollectorAgent", "ReadinessScorerAgent", "GapReporterAgent")
PACKAGE_AGENTS = ("ArtifactFetcherAgent", "CompletenessCheckerAgent", "PackageBuilderAgent")


def das_url() -> str:
    return os.environ.get("DAS_PUBLIC_URL", "https://das.k9x.ai").rstrip("/")


class ProgressMonitor:
    """Forwards agent loop events to the progress callback (live UI feed)."""

    _INTERESTING = {
        "loop_started", "hypothesis_generated", "validation_tool_invoked", "observation_evaluated",
        "loop_continued", "loop_finalized", "loop_escalated", "loop_failed", "AgentCompleted",
    }

    def __init__(self, callback):
        self._callback = callback

    def record_event(self, event: dict):
        evt_type = event.get("type", "")
        if evt_type not in self._INTERESTING:
            return
        ui_event = {"type": evt_type, "agent": event.get("agent", "?")}
        if event.get("iteration"):
            ui_event["iteration"] = event["iteration"]
        obs = event.get("observation", "")
        confidence = obs.get("confidence", "") if isinstance(obs, dict) else ""
        if not confidence and isinstance(obs, str):
            m = re.search(r"'confidence':\s*([\d.]+)", obs)
            confidence = round(float(m.group(1)), 2) if m else ""
        if confidence:
            ui_event["confidence"] = confidence
        self._callback(ui_event)


class ProcessStageOrchestrator(BaseOrchestrator):
    """Base for the DAS stage orchestrators. Subclasses set ``AGENTS`` (names) and ``layer``."""

    AGENTS: Tuple[str, ...] = READINESS_AGENTS + PACKAGE_AGENTS

    def __init__(self, config: Optional[Dict[str, Any]] = None,
                 progress_callback: Optional[Callable[[dict], None]] = None, **kwargs) -> None:
        config = config or {}
        # Orchestrators are not wrapped by governance by construction: build k9x Shield from
        # config so apply_shield() screens this boundary (security.shield, as for the agents).
        if "governance" not in kwargs and ((config.get("security") or {}).get("shield") or {}).get("enabled") is True:
            from k9_aif_abb.k9_security.vulnerability.shield_governance import ShieldGovernance
            kwargs["governance"] = ShieldGovernance(config)
        super().__init__(config=config, **kwargs)
        self._squads_dir = Path(__file__).resolve().parent.parent / "squads" / "yaml"
        self._agents_dir = Path(__file__).resolve().parent.parent / "agents" / "yaml"
        self._progress = progress_callback or (lambda e: None)
        self._monitor = ProgressMonitor(self._progress) if progress_callback else None

    # ── squads ────────────────────────────────────────────────────────
    def _load_squad(self, yaml_filename: str, squad_id: str):
        agent_loader = AgentLoader(self._agents_dir)
        registry = AgentRegistry()
        for name in self.AGENTS:
            cls = agent_loader.resolve_class(name)
            registry.register(
                name,
                lambda c=cls, n=name: c(config=agent_loader.merge_with_global(n, self.config),
                                        monitor=self._monitor),
            )
        return SquadLoader(registry).load_one(str(self._squads_dir / yaml_filename), squad_id)

    def _emit(self, event_type: str, **kwargs):
        self._progress({"type": event_type, "orchestrator": self.__class__.__name__, **kwargs})

    def _run_squad(self, squad, squad_name: str, payload: dict) -> dict:
        flow = getattr(squad, "flow", [])
        agents = [s.get("agent", "?") for s in flow]
        print(f"\n  ▶ Squad: {squad_name}  ({len(agents)} agents)", flush=True)
        self._emit("SquadStarted", squad=squad_name, agents=agents, total=len(agents))
        t0 = time.monotonic()
        result = squad.execute(payload)
        elapsed = time.monotonic() - t0
        print(f"  ✓ Squad: {squad_name}  done ({elapsed:.1f}s)\n", flush=True)
        self._emit("SquadCompleted", squad=squad_name, elapsed_s=round(elapsed, 1))
        return result

    # ── a gate's readiness + package ──────────────────────────────────
    def prepare_gate(self, gate_id: str, payload: dict, prior: dict) -> Tuple[dict, dict]:
        """GateReadiness then PackageAssembly for ``gate_id``; returns (readiness, package)."""
        from k9_dow.gates.gate_registry import DAS_GATES
        criteria = DAS_GATES[gate_id].entry_criteria
        base = {**payload, "gate_id": gate_id, "gate_criteria": criteria}
        readiness = self._run_squad(self._load_squad("gate_readiness_squad.yaml", "GateReadinessSquad"),
                                    "GateReadinessSquad", {**base, "prior_outputs": prior})
        package = self._run_squad(self._load_squad("package_assembly_squad.yaml", "PackageAssemblySquad"),
                                  "PackageAssemblySquad", {**base, "prior_outputs": {**prior, **readiness}})
        return readiness, package

    def publish_review(self, gate_id: str, job_id: str, readiness: dict, *, description: str,
                       artifacts: Iterable[Optional[str]], extra: Optional[Dict[str, Any]] = None) -> bool:
        """The HIL task for ``gate_id``: name-value summary + links to the package."""
        from k9_dow.config.process_model import load_process_model
        from k9_dow.gates import hil_gateway
        from k9_dow.gates.gate_registry import DAS_GATES
        from k9_dow.gates.review_summary import summarize_readiness
        gate = load_process_model().gate(gate_id)
        score = readiness.get("readiness_score", {}) if isinstance(readiness, dict) else {}
        summary = summarize_readiness(score.get("output") if isinstance(score, dict) else "",
                                      DAS_GATES[gate_id].entry_criteria,
                                      score.get("score") if isinstance(score, dict) else None) if readiness else {}
        published = hil_gateway.publish_gate_task(
            self.config, gate_id, job_id,
            title=f"{job_id} · {gate.title}",
            description=f"{description} Decision authority: {gate.authority}.",
            source_orchestrator=self.__class__.__name__,
            source_topic=f"das.{gate.prepared_by}",
            payload={"Gate": gate_id, **(extra or {}), **summary},
            artifacts=[a for a in artifacts if a],
        )
        if published:
            print(f"  → HIL task published: {gate.task_topic} (job={job_id})", flush=True)
            self._emit("HilTaskPublished", job_id=job_id, topic=gate.task_topic, gate_id=gate_id)
        return published

    # ── resuming after a human approval ───────────────────────────────
    @staticmethod
    def decision_text(payload: dict) -> Dict[str, Any]:
        """The one free-text input a resumed run receives: the reviewer's HIL comment."""
        return {"query": str((payload.get("decision") or {}).get("comment") or "")}

    def withhold_comment(self, payload: dict, shield: Dict[str, Any]) -> dict:
        """A comment Shield refuses never reaches the agents; the approval itself stands."""
        if shield.get("allowed", True):
            return payload
        decision = dict(payload.get("decision") or {})
        decision["comment"] = f"[comment withheld: {shield.get('reason', 'k9x Shield')}]"
        self._emit("ShieldWithheldComment", job_id=payload.get("job_id"), reason=shield.get("reason"))
        return {**payload, "decision": decision}


    @staticmethod
    def prior_from(stored: Dict[str, Any], keys: Iterable[str]) -> Dict[str, Any]:
        """Selected sections of an earlier run's stored result, as squad evidence."""
        out: Dict[str, Any] = {}
        for key in keys:
            section = stored.get(key)
            if isinstance(section, dict):
                out.update(section)
        return out

    def resume_context(self, payload: dict, approved_gate: str, earlier_runs: List[str]) -> Dict[str, Any]:
        """Source document, earlier runs' results and every recorded decision for this job."""
        from k9_dow.config.process_model import load_process_model
        from k9_dow.gates.hil_gateway import gate_decision_evidence, load_stage_result
        job_id = payload.get("job_id", "unknown")
        runs = {r: load_stage_result(self.config, job_id, r) or {} for r in earlier_runs}
        source = load_stage_result(self.config, job_id, "source") or {}
        # Decisions of record: every recorded decision on a gate an earlier run prepared
        # (the JCI review's JROCM included when it has come back), then the approval
        # that started this run.
        decisions: Dict[str, Any] = {}
        for gate in load_process_model().gates.values():
            if gate.prepared_by in earlier_runs and gate.id != approved_gate:
                rec = load_stage_result(self.config, job_id, f"gate-{gate.id}")
                if rec and rec.get("accepted", True):
                    decisions.update(gate_decision_evidence(gate.id, rec))
        decisions.update(gate_decision_evidence(approved_gate, payload.get("decision") or {}))
        requirement = runs.get("requirement") or {}
        return {"runs": runs, "source_markdown": source.get("markdown", ""),
                "document_title": requirement.get("document_title"),
                "filename": requirement.get("filename"), "decisions": decisions}

    def run_package(self, payload: dict, *, run: str, approved_gate: str, gate_id: str,
                    content: Tuple[str, str, str], prior_from: Dict[str, Iterable[str]],
                    description: str) -> Dict[str, Any]:
        """One run after a human approval: draft the documents (``content`` = squad yaml, squad id,
        result key), then judge, package and publish ``gate_id``. ``prior_from``: earlier run →
        sections of its stored result that are evidence here."""
        from k9_dow.config.process_model import load_process_model
        from k9_dow.gates.hil_gateway import save_stage_result
        from k9_dow.utils.icd_composer import icd_metadata

        job_id = payload.get("job_id", "unknown")
        decision = payload.get("decision") or {}
        t0 = time.monotonic()
        log.info("[%s] %s for job=%s (%s approved by %s)", self.layer, run, job_id, approved_gate, decision.get("actor"))
        self._emit("OrchestratorStarted", job_id=job_id, run=run, after_gate=approved_gate,
                   approved_by=decision.get("actor"))

        ctx = self.resume_context(payload, approved_gate, list(prior_from))
        prior = dict(ctx["decisions"])
        for earlier, keys in prior_from.items():
            prior.update(self.prior_from(ctx["runs"].get(earlier) or {}, keys))
        base = {**payload, "source_markdown": ctx["source_markdown"], "document_title": ctx["document_title"],
                "icd_metadata": icd_metadata(ctx["filename"] or "", job_id, run)}

        squad_file, squad_id, result_key = content
        drafted = self._run_squad(self._load_squad(squad_file, squad_id), squad_id, {**base, "prior_outputs": prior})
        readiness, package = self.prepare_gate(gate_id, base, {**prior, **drafted})

        result = {
            "job_id": job_id,
            "orchestrator": self.__class__.__name__,
            "orchestrator_run": run,
            "process_model": load_process_model().id,
            "status": "awaiting_gate",
            "gate_id": gate_id,
            "document_title": ctx["document_title"],
            "filename": ctx["filename"],
            "approved_gate": approved_gate,
            "decision": decision,
            "input_found": bool(ctx["runs"].get("requirement")),
            result_key: drafted,
            "gate_readiness": readiness,
            "review_package": package,
        }
        self._emit("OrchestratorCompleted", job_id=job_id, run=run, gate=gate_id,
                   elapsed_s=round(time.monotonic() - t0, 1))
        uri = save_stage_result(self.config, job_id, run, result)
        self.publish_review(gate_id, job_id, readiness, description=description,
                            extra={f"{approved_gate} approved by": decision.get("actor")},
                            artifacts=[f"{das_url()}/jobs/{job_id}/view/{run}",
                                       f"{das_url()}/jobs/{job_id}/docx/{run}", uri])
        return result
