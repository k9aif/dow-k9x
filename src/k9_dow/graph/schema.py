from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


# ─── Enums ───

class RequirementType(str, Enum):
    FUNCTIONAL = "functional"
    PERFORMANCE = "performance"
    INTERFACE = "interface"
    CONSTRAINT = "constraint"
    NFR = "nfr"


class VerificationMethod(str, Enum):
    TEST = "Test"
    DEMONSTRATION = "Demonstration"
    ANALYSIS = "Analysis"
    INSPECTION = "Inspection"


class RequirementStatus(str, Enum):
    PROPOSED = "proposed"
    REVIEWED = "reviewed"
    BASELINED = "baselined"
    SUPERSEDED = "superseded"


class RequirementMaturity(str, Enum):
    IDENTIFIED = "identified"
    ANALYZED = "analyzed"
    ALLOCATED = "allocated"
    VERIFIED = "verified"


class RequirementPriority(str, Enum):
    THRESHOLD = "threshold"
    OBJECTIVE = "objective"


class GateType(str, Enum):
    PREPARE_DECIDE = "PREPARE_DECIDE"
    REVIEW_APPROVE = "REVIEW_APPROVE"
    SIGN = "SIGN"


class GateAction(str, Enum):
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    RETURN_FOR_REWORK = "RETURN_FOR_REWORK"


class DriftSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


# ─── Canonical Entities (Section 4.1, SWP cut) ───

class CapabilityNeed(BaseModel):
    """Top of the traceability chain. On SWP, this is the stated gap that
    initiates the acquisition — not a formal ICD."""
    id: str
    title: str
    description: str
    source: str = ""
    status: str = "active"
    created: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CapabilityDocs(BaseModel):
    """CNS + living capability requirements. On SWP this is a continuously
    refined set, not a frozen ICD/CDD/CPD waterfall."""
    id: str
    title: str
    content: str
    doc_type: str = "CNS"
    version: str = "1.0"
    status: str = "draft"
    capability_need_id: str = ""
    created: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SERequirement(BaseModel):
    """The hinge of the traceability graph. Everything above is 'what capability
    do we need,' everything below is 'did we build it right.'"""
    id: str
    shall_text: str
    rationale: str = ""
    type: RequirementType = RequirementType.FUNCTIONAL
    verification_method: VerificationMethod = VerificationMethod.TEST
    status: RequirementStatus = RequirementStatus.PROPOSED
    priority: RequirementPriority = RequirementPriority.THRESHOLD
    maturity: RequirementMaturity = RequirementMaturity.IDENTIFIED
    owner: str = ""
    baseline_rev: str = ""
    source_hash: str = ""
    created: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class TechnicalBaselineItem(BaseModel):
    """A component/subsystem that an SERequirement is allocated to."""
    id: str
    name: str
    description: str = ""
    subsystem: str = ""
    baseline_rev: str = ""
    status: str = "active"


class DoDAFView(BaseModel):
    """A DoDAF architecture view (OV-1, SV-1, CV-2, etc.)."""
    id: str
    view_type: str
    title: str
    content: str = ""
    version: str = "1.0"
    status: str = "draft"
    created: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class TestCase(BaseModel):
    """Verification artifact linked to an SERequirement via VERIFIED_BY."""
    id: str
    title: str
    description: str = ""
    test_type: str = "functional"
    expected_result: str = ""
    status: str = "planned"
    last_run: Optional[datetime] = None
    result: Optional[str] = None


class VerificationEvent(BaseModel):
    """A specific execution of a TestCase."""
    id: str
    test_case_id: str
    executed_by: str = ""
    result: str = "pending"
    evidence: str = ""
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class FundingLine(BaseModel):
    """PPBE funding reference."""
    id: str
    program_element: str
    description: str = ""
    fiscal_year: str = ""
    amount: float = 0.0
    status: str = "current"


class SEPBaseline(BaseModel):
    """Systems Engineering Plan baseline reference."""
    id: str
    version: str
    description: str = ""
    approved_date: Optional[datetime] = None
    status: str = "current"


class GateCriterion(BaseModel):
    """An entry criterion for a HITL gate."""
    id: str
    gate_id: str
    description: str
    evidence_type: str = ""
    met: bool = False
    evidence_ref: str = ""


# ─── Relationship types (Neo4j edge labels) ───

RELATIONSHIP_TYPES = {
    "DECOMPOSES_TO": "CapabilityNeed → CapabilityDocs",
    "DERIVES": "CapabilityDocs → SERequirement",
    "DECOMPOSES_TO_CHILD": "SERequirement → SERequirement (parent/child tree)",
    "ALLOCATED_TO": "SERequirement → TechnicalBaselineItem",
    "EXPRESSED_IN": "SERequirement → DoDAFView",
    "VERIFIED_BY": "SERequirement → TestCase",
    "FUNDED_BY": "SERequirement → FundingLine",
    "BASELINED_IN": "SERequirement → SEPBaseline",
    "DEPENDS_ON": "SERequirement → SERequirement (lateral coupling)",
    "SUPERSEDES": "SERequirement → SERequirement (revision chain)",
    "EXECUTED_AS": "TestCase → VerificationEvent",
}
