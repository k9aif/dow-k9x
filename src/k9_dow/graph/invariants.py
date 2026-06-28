from __future__ import annotations

from dataclasses import dataclass


@dataclass
class InvariantResult:
    id: str
    name: str
    passed: bool
    violations: list
    query: str


# ─── The Four Trace Invariants (Section 4.3) ───
# Checked continuously by the Traceability Squad.

INVARIANT_1_ROOTLESS = """
// Invariant 1: Every requirement traces up to a stated capability need (no rootless reqs)
MATCH (s:SERequirement)
WHERE NOT (s)<-[:DERIVES|DECOMPOSES_TO_CHILD*]-(:CapabilityDocs)<-[:DECOMPOSES_TO]-(:CapabilityNeed)
  AND s.status <> 'superseded'
RETURN s.id AS id, s.shall_text AS shall_text
"""

INVARIANT_2_UNVERIFIED = """
// Invariant 2: Every SE requirement traces down to at least one test case (method-aware)
// Requirements with verification_method = 'Test' must have a VERIFIED_BY edge to a TestCase.
// Requirements with method = 'Analysis' or 'Inspection' must have a VERIFIED_BY edge
// to an appropriate verification artifact.
MATCH (s:SERequirement)
WHERE s.status <> 'superseded'
  AND NOT (s)-[:VERIFIED_BY]->()
RETURN s.id AS id, s.shall_text AS shall_text, s.verification_method AS method
"""

INVARIANT_3_ORPHAN_VIEWS = """
// Invariant 3: No orphan DoDAF view — every view references at least one live requirement
MATCH (v:DoDAFView)
WHERE NOT ()<-[:EXPRESSED_IN]-(v)
  AND v.status <> 'superseded'
RETURN v.id AS id, v.view_type AS view_type, v.title AS title
"""

INVARIANT_4_STALE_REFS = """
// Invariant 4: Funding and baseline references resolve to current, not superseded, records
MATCH (s:SERequirement)-[:FUNDED_BY]->(f:FundingLine)
WHERE f.status = 'superseded'
  AND s.status <> 'superseded'
RETURN s.id AS req_id, f.id AS funding_id, 'stale_funding' AS violation_type
UNION
MATCH (s:SERequirement)-[:BASELINED_IN]->(b:SEPBaseline)
WHERE b.status = 'superseded'
  AND s.status <> 'superseded'
RETURN s.id AS req_id, b.id AS funding_id, 'stale_baseline' AS violation_type
"""

ALL_INVARIANTS = {
    "INV-1": ("No rootless requirements", INVARIANT_1_ROOTLESS),
    "INV-2": ("No unverified requirements", INVARIANT_2_UNVERIFIED),
    "INV-3": ("No orphan DoDAF views", INVARIANT_3_ORPHAN_VIEWS),
    "INV-4": ("No stale funding/baseline references", INVARIANT_4_STALE_REFS),
}


def check_invariant(driver, invariant_id: str) -> InvariantResult:
    name, query = ALL_INVARIANTS[invariant_id]
    with driver.session() as session:
        result = session.run(query)
        violations = [dict(record) for record in result]
    return InvariantResult(
        id=invariant_id,
        name=name,
        passed=len(violations) == 0,
        violations=violations,
        query=query,
    )


def check_all_invariants(driver) -> list[InvariantResult]:
    return [check_invariant(driver, inv_id) for inv_id in ALL_INVARIANTS]
