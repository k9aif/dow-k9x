# SPDX-License-Identifier: Apache-2.0
"""HIL review tasks carry a readable name-value summary, not the scorer's raw Markdown, and link to a
human-readable document (SERVICE-VALIDATION: requirement package; MDD, MILESTONE-A, SRR: run package view and .docx)."""

from k9_dow.gates import hil_gateway
from k9_dow.gates.gate_registry import DAS_GATES
from k9_dow.gates.review_summary import summarize_readiness

# Shapes produced by the readiness scorer on the live deployment (JOB-20261008-2135EF, -66EB1F), trimmed.
PATHWAY_TABLE = """# PATHWAY-MILESTONE Readiness Assessment **Gate:** PATHWAY-MILESTONE
**Overall Readiness Score:** 75/100 **Status:** BLOCKED (Due to missing funding evidence)
| Criterion | Score | Rationale & Evidence Reference |
| :--- | :--- | :--- |
| **1. JROC validation approved** | **MET** | **Evidence:** `JROC-VALIDATION decision (human, of record)`<br>approved |
| **2. Pathway recommendation prepared** | **MET** | **Evidence:** `review_package` |
| **3. Funding line identified** | **NOT_MET** | **Evidence:** None found in provided artifacts. |
| **4. Artifact package complete for milestone** | **MET** | **Evidence:** `artifact_manifest` |
## Blockers
* **BLOCKER: Funding Line Not Identified**
    * **Impact:** The program cannot proceed to the next milestone.
## Summary for Decision Authority
**Recommendation for Decision Authority:** Do not proceed until the funding line is identified. The JROC approval does not waive it.
"""

JROC_HEADINGS = """| **3. DoDAF views generated and consistency-checked** | **PARTIALLY MET** | views missing |
| **4. No critical invariant violations** | **NOT_MET** | **Evidence:** `consistency_report`<br>**Rationale:** two |
**Overall Readiness Score: 67.5 / 100**
## 3. Blockers
1.  **Critical Invariant Violations (Criterion 4):**
    *   **Blocker:** Two critical incoherences (INC-01, INC-03) exist.
## 4. Recommendation for Decision Authority
**Recommendation:** **REJECT / HOLD**
"""


def test_pathway_assessment_becomes_name_value_pairs():
    s = summarize_readiness(PATHWAY_TABLE, DAS_GATES["PATHWAY-MILESTONE"].entry_criteria)
    assert s["Readiness"] == "75 / 100 — BLOCKED"
    assert s["1. JROC validation approved"] == "✓ Met"
    assert s["3. Funding line identified"] == "✗ Not met"
    assert s["Blockers"] == "Funding Line Not Identified"
    assert s["Recommendation"] == "Do not proceed until the funding line is identified"
    assert not any(c in v for v in s.values() for c in ("**", "|", "<br>", "##"))


def test_heading_style_assessment():
    s = summarize_readiness(JROC_HEADINGS, DAS_GATES["JROC-VALIDATION"].entry_criteria)
    assert s["Readiness"] == "67.5 / 100"
    assert s["3. DoDAF views generated and consistency-checked"] == "◐ Partially met"
    assert s["4. No critical invariant violations"] == "✗ Not met"
    assert s["Recommendation"] == "REJECT / HOLD"
    assert "Critical Invariant Violations" in s["Blockers"]


def test_unreadable_assessment_points_to_the_package():
    assert summarize_readiness("free text with no structure", ["Anything"]) == {
        "Readiness assessment": "See the review package (View link under Artifacts)"}


def test_milestone_a_task_payload_and_links(monkeypatch):
    from k9_dow.orchestrators.msa_orchestrator import MsaOrchestrator
    published = []

    class Squad:
        def __init__(self, out):
            self.out = out

        def execute(self, payload):
            return self.out

    monkeypatch.setattr(hil_gateway, "load_stage_result", lambda cfg, job, stage: {"filename": "F22.md"})
    monkeypatch.setattr(hil_gateway, "save_stage_result", lambda cfg, job, stage, res: "s3://jcids-output/x.json")
    monkeypatch.setattr(hil_gateway, "publish_gate_task", lambda cfg, gate, job, **kw: published.append((gate, kw)) or True)
    orch = MsaOrchestrator(config={})
    gate = Squad({"readiness_score": {"output": PATHWAY_TABLE, "score": 75}})
    monkeypatch.setattr(orch, "_load_squad", lambda f, sid: gate if sid == "GateReadinessSquad" else Squad({}))
    orch.execute_flow(hil_gateway.gate_approved_event("MDD", {
        "correlation_id": "job-7", "action": "complete", "actor": "mda@k9x.ai", "status": "completed",
        "comment": None, "result": None, "decided_at": "2026-10-08T12:00:00+00:00"}))
    gate_id, kw = published[0]
    assert gate_id == "MILESTONE-A" and kw["payload"]["Gate"] == "MILESTONE-A"
    assert kw["payload"]["MDD approved by"] == "mda@k9x.ai"
    assert "readiness_score" not in kw["payload"]                       # no raw Markdown in the task
    assert kw["artifacts"][0].endswith("/jobs/job-7/view/msa")
    assert kw["artifacts"][1].endswith("/jobs/job-7/docx/msa")
    assert "Milestone Decision Authority" in kw["description"]


def test_requirement_publishes_service_validation_and_parallel_jci(monkeypatch):
    from k9_dow.orchestrators.requirement_orchestrator import RequirementOrchestrator
    published = []
    monkeypatch.setattr(hil_gateway, "publish_gate_task", lambda cfg, gate, job, **kw: published.append((gate, kw)) or True)
    monkeypatch.setattr(hil_gateway, "save_stage_result", lambda cfg, job, stage, res: None)
    orch = RequirementOrchestrator(config={})
    orch._publish_hil_tasks("job-9", {
        "gate_readiness": {"readiness_score": {"output": JROC_HEADINGS}},
        "joint_review": {"jsd": {"output": "## Recommended Joint Staffing Designator\nFCB Interest"}},
        "screening": {"status": "clean", "sections_screened": 7, "report_uri": "s3://r.md"}}, "s3://x/req.md")
    (g1, sv), (g2, jci) = published
    assert g1 == "SERVICE-VALIDATION" and sv["payload"]["Gate"] == "SERVICE-VALIDATION"
    assert sv["payload"]["Document screening"] == "no warnings (7 sections)"
    assert sv["artifacts"][0].endswith("/jobs/job-9/view/requirement") and "s3://r.md" in sv["artifacts"]
    assert "gap_summary" not in sv["payload"] and "readiness_score" not in sv["payload"]
    assert g2 == "JCI-REVIEW" and jci["payload"]["Recommended JSD"] == "FCB Interest"
    assert "never holds" in jci["description"] and jci["artifacts"][0].endswith("/jobs/job-9/view/jsd")
