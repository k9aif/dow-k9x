from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field

from k9_dow.graph.schema import GateType, GateAction


class GateDefinition(BaseModel):
    """A HITL gate definition. Gates are first-class objects — not afterthoughts.

    Rule: any gate with non_delegable=True causes the orchestrator to halt
    and require a human token before continuing. No agent may synthesize
    or impersonate that token.
    """
    id: str
    name: str
    type: GateType
    owning_orchestrator: str
    agent_role: str = "PREPARE_ONLY"
    human_role: str = "DECISION_AUTHORITY"
    entry_criteria: list[str] = Field(default_factory=list)
    human_actions: list[GateAction] = Field(
        default_factory=lambda: [GateAction.APPROVE, GateAction.REJECT, GateAction.RETURN_FOR_REWORK]
    )
    non_delegable: bool = True


class GateDecision(BaseModel):
    """An immutable record of a human decision at a gate."""
    gate_id: str
    action: GateAction
    decided_by: str
    rationale: str
    evidence_package_ref: str = ""
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class GateStatus(BaseModel):
    """Runtime state of a gate during pipeline execution."""
    gate_id: str
    state: str = "pending"
    evidence_package: Optional[dict] = None
    criteria_met: dict[str, bool] = Field(default_factory=dict)
    decision: Optional[GateDecision] = None

    @property
    def ready_for_human(self) -> bool:
        return all(self.criteria_met.values()) and len(self.criteria_met) > 0

    @property
    def is_resolved(self) -> bool:
        return self.decision is not None
