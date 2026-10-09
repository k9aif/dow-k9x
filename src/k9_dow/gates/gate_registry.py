from __future__ import annotations

import threading

from k9_dow.gates.gate_model import GateDefinition, GateStatus, GateDecision
from k9_dow.graph.schema import GateType, GateAction


class GateAlreadyDecidedError(Exception):
    """Raised when record_decision() is called on a gate whose state is
    already "resolved" -- the caller lost a race with another
    concurrent decision on the same gate. The caller receives this
    instead of silently overwriting the existing decision."""
    pass


# ─── Gates from the process model ───
# Every gate of the current process (config/process_model.yaml): criteria, authority and
# sources come from the file, so a policy change is an edit there, not here. All are
# non-delegable: an agent prepares, an identified person decides.

def _process_gates() -> dict[str, GateDefinition]:
    from k9_dow.config.process_model import load_process_model
    pm = load_process_model()
    return {
        g.id: GateDefinition(
            id=g.id,
            name=g.title,
            type=GateType(g.type),
            owning_orchestrator=g.owner,
            entry_criteria=list(g.entry_criteria),
            authority=g.authority,
            blocking=g.blocking,
            decision_record=g.decision_record,
            evidence=list(g.evidence),
            sources=list(g.sources),
            process_model=pm.id,
            non_delegable=True,
        )
        for g in pm.gates.values()
    }


PROCESS_GATES: dict[str, GateDefinition] = _process_gates()

# ─── Legacy (JCIDS-era) gates ───
# Used by the JCIDS-era orchestrators until they move to the process model (build step 4),
# then removed. New code reads gates from the process model.

LEGACY_GATES: dict[str, GateDefinition] = {
    "JROC-VALIDATION": GateDefinition(
        id="JROC-VALIDATION",
        name="JROC Validation Prep",
        type=GateType.PREPARE_DECIDE,
        owning_orchestrator="jcids",
        entry_criteria=[
            "Capability need statement complete",
            "Requirements traceability coverage >= 90%",
            "DoDAF views generated and consistency-checked",
            "No critical invariant violations",
            "Evidence package assembled",
        ],
        criterion_weights=[20, 20, 20, 30, 10],
        non_delegable=True,
    ),
    "PATHWAY-MILESTONE": GateDefinition(
        id="PATHWAY-MILESTONE",
        name="Acquisition Pathway / Milestone Decision",
        type=GateType.PREPARE_DECIDE,
        owning_orchestrator="acquisition",
        entry_criteria=[
            "JROC validation approved",
            "Pathway recommendation prepared",
            "Funding line identified",
            "JCIDS review package available (ICD, readiness assessment, artifact manifest)",
        ],
        criterion_weights=[25, 25, 25, 25],
        non_delegable=True,
    ),
    "SE-REVIEW-SFR": GateDefinition(
        id="SE-REVIEW-SFR",
        name="System Functional Review",
        type=GateType.REVIEW_APPROVE,
        owning_orchestrator="se",
        entry_criteria=[
            "Functional allocation complete",
            "Interface requirements defined",
            "No unallocated requirements",
        ],
        non_delegable=True,
    ),
    "SE-REVIEW-PDR": GateDefinition(
        id="SE-REVIEW-PDR",
        name="Preliminary Design Review",
        type=GateType.REVIEW_APPROVE,
        owning_orchestrator="se",
        entry_criteria=[
            "Preliminary design artifacts complete",
            "Requirements allocated to components",
            "Risk assessment current",
        ],
        non_delegable=True,
    ),
    "SE-REVIEW-CDR": GateDefinition(
        id="SE-REVIEW-CDR",
        name="Critical Design Review",
        type=GateType.REVIEW_APPROVE,
        owning_orchestrator="se",
        entry_criteria=[
            "Detailed design complete",
            "Test procedures drafted",
            "Manufacturing/build readiness assessed",
        ],
        non_delegable=True,
    ),
    "SE-REVIEW-TRR": GateDefinition(
        id="SE-REVIEW-TRR",
        name="Test Readiness Review",
        type=GateType.REVIEW_APPROVE,
        owning_orchestrator="se",
        entry_criteria=[
            "All test cases defined",
            "Test environment ready",
            "100% verification coverage",
        ],
        non_delegable=True,
    ),
}


DAS_GATES: dict[str, GateDefinition] = {**LEGACY_GATES, **PROCESS_GATES}


class GateRegistry:
    """Registry of all HITL gates in the DAS pipeline.
    Enforces non-delegable hard-stops."""

    def __init__(self) -> None:
        self._gates = dict(DAS_GATES)
        self._runtime: dict[str, GateStatus] = {}
        self._decision_lock = threading.Lock()

    def get_gate(self, gate_id: str) -> GateDefinition:
        return self._gates[gate_id]

    def list_gates(self, orchestrator: str | None = None) -> list[GateDefinition]:
        gates = list(self._gates.values())
        if orchestrator:
            gates = [g for g in gates if g.owning_orchestrator == orchestrator]
        return gates

    def init_gate(self, gate_id: str) -> GateStatus:
        gate_def = self._gates[gate_id]
        status = GateStatus(
            gate_id=gate_id,
            state="pending",
            criteria_met={c: False for c in gate_def.entry_criteria},
        )
        self._runtime[gate_id] = status
        return status

    def update_criterion(self, gate_id: str, criterion: str, met: bool) -> GateStatus:
        status = self._runtime[gate_id]
        status.criteria_met[criterion] = met
        if status.ready_for_human:
            status.state = "awaiting_human"
        return status

    def record_decision(self, gate_id: str, decision: GateDecision) -> GateStatus:
        """Atomically transition a gate to "resolved". Guarded by a lock
        plus an explicit state check so two concurrent decisions on the
        same gate cannot both silently commit: the first to acquire the
        lock wins, and any later caller sees the gate already resolved
        and gets GateAlreadyDecidedError rather than overwriting the
        winning decision. Closes the compare-and-swap gap previously
        disclosed for this registry."""
        gate_def = self._gates[gate_id]
        if gate_def.non_delegable and not decision.decided_by:
            raise ValueError(f"Gate {gate_id} is non-delegable — requires identified human authority")

        with self._decision_lock:
            status = self._runtime[gate_id]
            if status.state == "resolved":
                existing_action = status.decision.action if status.decision else "unknown"
                raise GateAlreadyDecidedError(
                    f"Gate {gate_id!r} was already resolved (existing decision: "
                    f"{existing_action}); conflicting decision {decision.action!r} rejected"
                )
            status.decision = decision
            status.state = "resolved"
            return status

    def may_proceed(self, gate_id: str) -> bool:
        status = self._runtime.get(gate_id)
        if not status:
            return False
        if not status.is_resolved:
            return False
        return status.decision.action == GateAction.APPROVE
