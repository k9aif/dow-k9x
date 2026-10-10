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
from datetime import datetime, timezone
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
        self._run_config: Optional[Dict[str, Any]] = None   # set while a governance override applies
        self._active_job_id: Optional[str] = None

    # ── squads ────────────────────────────────────────────────────────
    def _load_squad(self, yaml_filename: str, squad_id: str):
        agent_loader = AgentLoader(self._agents_dir)
        registry = AgentRegistry()
        # A run resumed with a governance override uses a config with that one check relaxed.
        config = getattr(self, "_run_config", None) or self.config
        for name in self.AGENTS:
            cls = agent_loader.resolve_class(name)
            registry.register(
                name,
                lambda c=cls, n=name: self._withdrawable(
                    c(config=agent_loader.merge_with_global(n, config), monitor=self._monitor)),
            )
        return SquadLoader(registry).load_one(str(self._squads_dir / yaml_filename), squad_id)

    def _withdrawable(self, agent):
        """Before the agent runs, stop if its job has been withdrawn (Jobs in Pipeline ›
        Withdraw): a running stage stops at its next agent. The agent's own execute,
        governance included, is unchanged."""
        run = agent.execute

        def execute(payload, _run=run):
            from k9_dow.gates.hil_gateway import JobWithdrawn, withdrawn
            job_id = (payload or {}).get("job_id") or self._active_job_id
            wd = withdrawn(self.config, job_id)
            if wd:
                raise JobWithdrawn(f"job {job_id} withdrawn by {wd.get('by')} at {wd.get('at')}")
            return _run(payload)
        agent.execute = execute
        return agent

    def _emit(self, event_type: str, **kwargs):
        self._progress({"type": event_type, "orchestrator": self.__class__.__name__, **kwargs})

    def _run_squad(self, squad, squad_name: str, payload: dict) -> dict:
        self._active_job_id = payload.get("job_id") or self._active_job_id
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
    def prepare_gate(self, gate_id: str, payload: dict, prior: dict,
                     readiness: Optional[dict] = None, partial: Optional[dict] = None) -> Tuple[dict, dict]:
        """GateReadiness then PackageAssembly for ``gate_id``; returns (readiness, package).
        ``readiness`` given (a held run resuming): that squad is not run again. ``partial`` collects
        each finished squad, so a hold keeps the work already done."""
        from k9_dow.gates.gate_registry import DAS_GATES
        criteria = DAS_GATES[gate_id].entry_criteria
        base = {**payload, "gate_id": gate_id, "gate_criteria": criteria}
        if readiness is None:
            readiness = self._run_squad(self._load_squad("gate_readiness_squad.yaml", "GateReadinessSquad"),
                                        "GateReadinessSquad", {**base, "prior_outputs": prior})
        if partial is not None:
            partial["gate_readiness"] = readiness
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
        # Decisions of record: every decision recorded for this job so far, in process order
        # (Service validation, the JCI review's JROCM when it has come back, MDD, ...), then
        # the approval that started this run. A later gate (e.g. the SRR) cites them all.
        decisions: Dict[str, Any] = {}
        for gate in load_process_model().gates.values():
            if gate.id != approved_gate:
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
        from k9_dow.gates.hil_gateway import JobWithdrawn, save_stage_result
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
        override = payload.get("governance_override")
        partial: Dict[str, Any] = {}
        if override:
            # Resuming a held run: reuse what it finished, relax only the overridden check.
            from k9_dow.gates.hil_gateway import load_stage_result
            hold = load_stage_result(self.config, job_id, "hold") or {}
            partial = dict(hold.get("partial") or {}) if hold.get("run") == run else {}
            self._run_config = config_without_check(self.config, override.get("check"))
            self._emit("GovernanceOverrideApplied", job_id=job_id, run=run, check=override.get("check"),
                       approved_by=override.get("actor"))
        try:
            drafted = partial.get(result_key)
            if drafted is None:
                drafted = self._run_squad(self._load_squad(squad_file, squad_id), squad_id,
                                          {**base, "prior_outputs": prior})
                partial[result_key] = drafted
            readiness, package = self.prepare_gate(gate_id, base, {**prior, **drafted},
                                                   readiness=partial.get("gate_readiness"), partial=partial)
        except JobWithdrawn:
            raise                      # withdrawn: no error record, no retry (orchestrator process)
        except PermissionError as exc:
            # Governance refused an agent's input mid-run: hold, keep the work, ask a person.
            return self.hold_for_governance(job_id, run, approved_gate, decision, gate_id, str(exc), partial)
        except Exception as exc:
            # Recorded so Jobs in Pipeline shows the failure and offers the admin a retry,
            # instead of the run looking "running" forever.
            save_stage_result(self.config, job_id, run, {
                "job_id": job_id, "orchestrator": self.__class__.__name__, "orchestrator_run": run,
                "status": "error", "detail": str(exc)[:500], "approved_gate": approved_gate,
                "failed_at": datetime.now(timezone.utc).isoformat()})
            self._emit("OrchestratorFailed", job_id=job_id, run=run, error=str(exc)[:300])
            raise
        finally:
            self._run_config = None

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
        if override:
            result["governance_override"] = override
        self._emit("OrchestratorCompleted", job_id=job_id, run=run, gate=gate_id,
                   elapsed_s=round(time.monotonic() - t0, 1))
        uri = save_stage_result(self.config, job_id, run, result)
        extra = {f"{approved_gate} approved by": decision.get("actor")}
        if override:
            extra["Governance override"] = (f"{override.get('check')} relaxed for this stage by "
                                            f"{override.get('actor')} ({(override.get('decided_at') or '')[:16]})")
        self.publish_review(gate_id, job_id, readiness, description=description, extra=extra,
                            artifacts=[f"{das_url()}/jobs/{job_id}/view/{run}",
                                       f"{das_url()}/jobs/{job_id}/docx/{run}", uri])
        return result

    def hold_for_governance(self, job_id: str, run: str, approved_gate: str, decision: dict, gate_id: str,
                            reason: str, partial: dict) -> Dict[str, Any]:
        """Save the held run (with its finished squads), raise a Governance hold task in K9X HIL, and
        publish a governance alert. The job is kept; a person decides to override or stop."""
        from k9_dow.gates import hil_gateway
        check = hil_gateway.hold_check(reason)
        at = datetime.now(timezone.utc).isoformat()
        held = {"job_id": job_id, "orchestrator": self.__class__.__name__, "orchestrator_run": run,
                "status": "held", "gate_id": gate_id, "check": check, "reason": reason[:500],
                "approved_gate": approved_gate, "held_at": at}
        hil_gateway.save_stage_result(self.config, job_id, run, held)
        hil_gateway.save_stage_result(self.config, job_id, "hold", {
            "run": run, "check": check, "reason": reason[:500], "at": at, "approved_gate": approved_gate,
            "decision": decision, "partial": partial, "orchestrator": self.__class__.__name__})
        print(f"  ⏸ Governance hold job={job_id} run={run}: {reason[:160]}", flush=True)
        self._emit("GovernanceHold", job_id=job_id, run=run, check=check, reason=reason[:300])
        hil_gateway.publish_gate_task(
            self.config, hil_gateway.GOVERNANCE_HOLD, job_id,
            title=f"{job_id} · Governance hold: {check} at {run}",
            description=(f"k9x governance refused an agent's input while preparing the {gate_id} package "
                         f"(run {run}). The job and the work already done are kept. Approve to override "
                         f"{check} for this job and this run only (recorded with your name and comment); "
                         f"reject to stop the job here."),
            source_orchestrator=self.__class__.__name__, source_topic=f"das.{run}",
            payload={"Run": run, "Preparing gate": gate_id, "Check": check, "Reason": reason[:300],
                     "Work kept": ", ".join(partial) or "none"},
            artifacts=[f"{das_url()}/app"], priority="high",
        )
        hil_gateway.record_governance_alert(self.config, {
            "type": "governance_hold", "job_id": job_id, "run": run, "gate_id": gate_id,
            "check": check, "reason": reason[:300]})
        return held


def config_without_check(config: Dict[str, Any], check: Optional[str]) -> Dict[str, Any]:
    """A copy of ``config`` with one governance check relaxed (a human override for one run)."""
    import copy
    cfg = copy.deepcopy(config)
    if not check:
        return cfg
    shield = ((cfg.get("security") or {}).get("shield") or {})
    for side in ("ingress", "egress"):
        checks = (shield.get(side) or {}).get("checks")
        if isinstance(checks, list) and check in checks:
            shield[side]["checks"] = [c for c in checks if c != check]
    if check == "GraniteGuardian":
        ((cfg.setdefault("governance", {})).setdefault("guardian", {}))["enabled"] = False
    return cfg
