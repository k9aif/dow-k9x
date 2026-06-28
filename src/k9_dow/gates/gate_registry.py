from __future__ import annotations

from k9_dow.gates.gate_model import GateDefinition, GateStatus, GateDecision
from k9_dow.graph.schema import GateType, GateAction


# ─── Non-delegable HITL Gates (minimum set from spec Section 6) ───

DAS_GATES: dict[str, GateDefinition] = {
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
            "Artifact package complete for milestone",
        ],
        non_delegable=True,
    ),
    "SE-REVIEW-SRR": GateDefinition(
        id="SE-REVIEW-SRR",
        name="System Requirements Review",
        type=GateType.REVIEW_APPROVE,
        owning_orchestrator="se",
        entry_criteria=[
            "All SE requirements baselined",
            "Requirements decomposition complete",
            "Verification methods assigned",
            "Traceability invariants pass",
        ],
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


class GateRegistry:
    """Registry of all HITL gates in the DAS pipeline.
    Enforces non-delegable hard-stops."""

    def __init__(self) -> None:
        self._gates = dict(DAS_GATES)
        self._runtime: dict[str, GateStatus] = {}

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
        gate_def = self._gates[gate_id]
        if gate_def.non_delegable and not decision.decided_by:
            raise ValueError(f"Gate {gate_id} is non-delegable — requires identified human authority")

        status = self._runtime[gate_id]
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
