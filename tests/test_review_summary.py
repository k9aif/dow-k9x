# SPDX-License-Identifier: Apache-2.0
"""HIL review tasks carry a readable name-value summary, not the scorer's raw Markdown, and link to a
human-readable document (JROC: ICD; PATHWAY-MILESTONE: Milestone package view and .docx)."""

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


def test_pathway_task_payload_and_links(monkeypatch):
    from k9_dow.orchestrators import acquisition_orchestrator as acq_mod
    published = []

    class Squad:
        def __init__(self, out):
            self.out = out

        def execute(self, payload):
            return self.out

    monkeypatch.setattr(hil_gateway, "load_stage_result", lambda cfg, job, stage: {"filename": "F22.md"})
    monkeypatch.setattr(hil_gateway, "save_stage_result", lambda cfg, job, stage, res: "s3://jcids-output/x.json")
    monkeypatch.setattr(hil_gateway, "publish_gate_task", lambda cfg, gate, job, **kw: published.append(kw) or True)
    orch = acq_mod.AcquisitionOrchestrator(config={})
    gate = Squad({"readiness_score": {"output": PATHWAY_TABLE}})
    monkeypatch.setattr(orch, "_load_squad", lambda f, sid: gate if sid == "GateReadinessSquad" else Squad({}))
    orch.execute_flow(hil_gateway.gate_approved_event("JROC-VALIDATION", {
        "correlation_id": "job-7", "action": "complete", "actor": "reviewer@k9x.ai", "status": "completed",
        "comment": None, "result": None, "decided_at": "2026-10-08T12:00:00+00:00"}))
    kw = published[0]
    assert kw["payload"]["Gate"] == "PATHWAY-MILESTONE"
    assert kw["payload"]["Readiness"] == "75 / 100 — BLOCKED"
    assert kw["payload"]["JROC approved by"] == "reviewer@k9x.ai"
    assert "readiness_score" not in kw["payload"]                       # no raw Markdown in the task
    assert kw["artifacts"][0].endswith("/jobs/job-7/view/milestone")
    assert kw["artifacts"][1].endswith("/jobs/job-7/docx/milestone")


def test_jroc_task_payload(monkeypatch):
    from k9_dow.orchestrators import jcids_orchestrator as jc_mod
    published = []
    monkeypatch.setattr(jc_mod, "publish_gate_task", lambda cfg, gate, job, **kw: published.append(kw) or True,
                        raising=False)
    monkeypatch.setattr(hil_gateway, "publish_gate_task", lambda cfg, gate, job, **kw: published.append(kw) or True)
    orch = jc_mod.JcidsOrchestrator.__new__(jc_mod.JcidsOrchestrator)
    orch.config, orch._progress = {}, (lambda e: None)
    orch._publish_hil_task("job-9", {"gate_readiness": {"readiness_score": {"output": JROC_HEADINGS}}}, "s3://x/ICD.md")
    kw = published[0]
    assert kw["payload"]["Gate"] == "JROC-VALIDATION"
    assert kw["payload"]["Readiness"] == "67.5 / 100"
    assert "gap_summary" not in kw["payload"] and "readiness_score" not in kw["payload"]
    assert kw["artifacts"][0].endswith("/jobs/job-9/view/icd")
