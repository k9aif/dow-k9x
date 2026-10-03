# SPDX-License-Identifier: Apache-2.0
# K9-AIF Framework
"""ICD quality check: deterministic parts (no model)."""

from k9_dow.quality import icd_grader as g

SOURCE = """# CDD
| KPP 3: Mobility | Sustained road speed of 65 mph |
Recent simulations found delays in subsystem initialization and inconsistent hydraulic readings.
"""

ICD = '''# Initial Capabilities Document (ICD)
## 1. Architecture Views
- id: CN-001, title: Mobility, description: road speed
| CAP-001 | "KPP 3: Mobility Sustained road speed of 65 mph" |
Evidence: "inconsistent hydraulic readings" and "subsystem initialization delays were observed"
Names "OV-2") does not match "SV-1" -- not quotations
## 2. Gate Readiness Assessment
Report: "No generated views were provided for analysis in this report"
'''


def test_citations_only_from_the_views_and_markdown_ignored():
    r = g.citation_accuracy(SOURCE, ICD)
    assert r["checked"] == 3                      # gate-readiness self-quote and name gaps excluded
    assert r["found"] == 2                        # table row (markdown ignored) + exact phrase
    assert r["not_found"] == ["subsystem initialization delays were observed"]   # a paraphrase in quotes


def test_completeness_lists_missing_sections():
    r = g.completeness(ICD + "\n### 1.1 Model Elements\n### 1.3 Cross-View Consistency Report\n")
    assert 0 < r["score"] < 1
    assert "Model elements" not in r["missing"] and "Readiness score" in r["missing"]


def test_claims_and_json_parsing():
    assert [c["id"] for c in g._claims(ICD)] == ["CN-001"]
    out = g._parse_json_array('<think>reasoning [not json]</think> [{"id": "CN-001", "verdict": "supported"}]')
    assert out == [{"id": "CN-001", "verdict": "supported"}]


def test_grade_combines_scores(monkeypatch):
    monkeypatch.setattr(g, "faithfulness", lambda s, i, c: {"score": 0.5, "judged": 2, "supported": 1})
    r = g.grade(SOURCE, ICD, {"inference": {"llm_factory": {"models": {"judge": {"model": "deepseek-r1:32b"}}}}})
    assert r["scored_by"] == "deepseek-r1:32b" and r["overall"] is not None
