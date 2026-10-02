# SPDX-License-Identifier: Apache-2.0
# K9-AIF Framework
"""JCIDS → JROC (HIL) → Acquisition → PATHWAY-MILESTONE (HIL) → SE.

No Kafka, no S3, no model: the HIL reply is turned into the event the Router
routes, the stages run with their squads and storage faked."""

import pytest

from k9_dow.gates import hil_gateway
from k9_dow.gates.hil_gateway import GATE_INPUT_STAGE, GATE_TOPICS, REPLY_TOPIC_TO_GATE, gate_approved_event
from k9_dow.routers.das_router import DAS_TOPICS, DasRouter


def hil_reply(job_id, action="complete", actor="reviewer@k9x.ai"):
    # Shape published by K9X HIL v1.2.0 (backend/hil_reply.py build_reply_event)
    return {"correlation_id": job_id, "action": action, "actor": actor, "status": "completed",
            "comment": None, "result": None, "decided_at": "2026-10-02T12:00:00+00:00"}


def test_every_gate_has_a_reply_topic_and_an_input_stage():
    assert set(GATE_TOPICS) == set(GATE_INPUT_STAGE) == {"JROC-VALIDATION", "PATHWAY-MILESTONE"}
    assert REPLY_TOPIC_TO_GATE["das.jroc.replies"] == "JROC-VALIDATION"
    assert REPLY_TOPIC_TO_GATE["das.pathway.replies"] == "PATHWAY-MILESTONE"


@pytest.mark.parametrize("gate_id,next_topic", [
    ("JROC-VALIDATION", DAS_TOPICS["acquisition"]),
    ("PATHWAY-MILESTONE", DAS_TOPICS["se"]),
])
def test_approval_routes_to_the_next_stage(gate_id, next_topic):
    event = gate_approved_event(gate_id, hil_reply("job-1"))
    assert event["event_type"] == "gate_approved" and event["job_id"] == "job-1"
    assert event["decision"]["actor"] == "reviewer@k9x.ai"
    assert DasRouter(config={}).route(event)["route_to"] == next_topic


def test_approvers_unset_means_any(monkeypatch):
    monkeypatch.delenv("DAS_HIL_APPROVERS", raising=False)
    assert hil_gateway.approvers() is None
    monkeypatch.setenv("DAS_HIL_APPROVERS", "A@k9x.ai, b@k9x.ai")
    assert hil_gateway.approvers() == {"a@k9x.ai", "b@k9x.ai"}


class FakeSquad:
    def __init__(self, name):
        self.name, self.flow, self.seen = name, [{"agent": "X"}], []

    def execute(self, payload):
        self.seen.append(payload)
        return {"readiness_score": {"output": f"{self.name} ok"}}


def test_acquisition_resumes_from_stored_jcids_and_raises_its_gate(monkeypatch):
    from k9_dow.orchestrators import acquisition_orchestrator as acq_mod

    stored, published, events = {}, [], []
    monkeypatch.setattr(hil_gateway, "load_stage_result",
                        lambda cfg, job, stage: {"document_title": "FIREBIRD", "gate_readiness": {"g": 1}})
    monkeypatch.setattr(hil_gateway, "save_stage_result",
                        lambda cfg, job, stage, res: stored.setdefault(stage, res) and "s3://x")
    monkeypatch.setattr(hil_gateway, "publish_gate_task",
                        lambda cfg, gate, job, **kw: published.append((gate, job, kw)) or True)
    squads = {}
    orch = acq_mod.AcquisitionOrchestrator(config={}, progress_callback=events.append)
    monkeypatch.setattr(orch, "_load_squad", lambda f, sid: squads.setdefault(sid, FakeSquad(sid)))

    event = gate_approved_event("JROC-VALIDATION", hil_reply("job-7"))
    result = orch.execute_flow(event)

    assert result["status"] == "awaiting_gate" and result["gate_id"] == "PATHWAY-MILESTONE"
    assert result["jroc_decision"]["actor"] == "reviewer@k9x.ai" and result["input_found"]
    first = squads["GateReadinessSquad"].seen[0]
    assert first["gate_id"] == "PATHWAY-MILESTONE" and "Funding line identified" in first["gate_criteria"]
    assert stored["acquisition"]["job_id"] == "job-7"
    assert published[0][0] == "PATHWAY-MILESTONE" and published[0][1] == "job-7"
    types = [e["type"] for e in events]
    assert types[0] == "OrchestratorStarted" and "HilTaskPublished" in types
    assert all(e["orchestrator"] == "AcquisitionOrchestrator" for e in events)


def test_se_is_a_labelled_demonstration_endpoint(monkeypatch):
    from k9_dow.orchestrators.se_orchestrator import SeOrchestrator
    saved = {}
    monkeypatch.setattr(hil_gateway, "save_stage_result", lambda cfg, job, stage, res: saved.update({stage: res}))
    events = []
    result = SeOrchestrator(config={}, progress_callback=events.append).execute_flow(
        gate_approved_event("PATHWAY-MILESTONE", hil_reply("job-7", actor="mda@k9x.ai")))
    assert result["status"] == "pipeline_complete" and result["demo_stub"] is True
    assert result["target_review"] == "SE-REVIEW-SRR"
    assert result["milestone_decision"]["actor"] == "mda@k9x.ai"
    assert [e["type"] for e in events] == ["OrchestratorStarted", "OrchestratorCompleted"]
    assert saved["se"]["demo_stub"] is True


def _history(monkeypatch, stored):
    monkeypatch.setattr(hil_gateway, "load_stage_result", lambda cfg, job, stage: stored.get(stage))
    h = hil_gateway.job_history({}, "job-9", list(stored))
    return [(s["step"], s["state"], s.get("actor")) for s in h["steps"]]


def test_history_pending_jroc(monkeypatch):
    assert _history(monkeypatch, {"jcids": {"status": "awaiting_gate"}})[:3] == [
        ("jcids", "done", None), ("JROC-VALIDATION", "pending", None), ("acquisition", "not_reached", None)]


def test_history_uses_decision_file_or_next_stage(monkeypatch):
    # Decision recorded only inside the next stage (decided before decision files existed)
    steps = _history(monkeypatch, {"jcids": {"status": "awaiting_gate"},
                                   "acquisition": {"status": "awaiting_gate",
                                                   "jroc_decision": {"action": "complete", "actor": "a@k9x.ai"}}})
    assert steps[1] == ("JROC-VALIDATION", "approved", "a@k9x.ai")
    assert steps[3] == ("PATHWAY-MILESTONE", "pending", None)
    # Rejection kept by the Router's decision file
    steps = _history(monkeypatch, {"jcids": {"status": "awaiting_gate"},
                                   "gate-JROC-VALIDATION": {"action": "reject", "actor": "b@k9x.ai", "accepted": True}})
    assert steps[1] == ("JROC-VALIDATION", "reject", "b@k9x.ai") and steps[2][1] == "not_reached"


def test_history_full_run_marks_se_demo(monkeypatch):
    steps = _history(monkeypatch, {"jcids": {"status": "awaiting_gate"}, "acquisition": {"status": "awaiting_gate"},
                                   "gate-JROC-VALIDATION": {"action": "complete", "actor": "a@k9x.ai"},
                                   "gate-PATHWAY-MILESTONE": {"action": "complete", "actor": "m@k9x.ai"},
                                   "se": {"status": "pipeline_complete", "demo_stub": True}})
    assert [s[1] for s in steps] == ["done", "approved", "done", "approved", "done"]


# ── Manual resume: DAS admin starts the next stage after a HIL approval ──

def test_history_offers_next_action_until_started(monkeypatch):
    stored = {"jcids": {"status": "awaiting_gate"},
              "gate-JROC-VALIDATION": {"action": "complete", "actor": "a@k9x.ai"}}
    monkeypatch.setattr(hil_gateway, "load_stage_result", lambda cfg, job, stage: stored.get(stage))
    h = hil_gateway.job_history({}, "job-9", list(stored))
    assert h["next_action"] == {"gate": "JROC-VALIDATION", "stage": "acquisition"}
    stored["started-acquisition"] = {"by": "admin"}
    h = hil_gateway.job_history({}, "job-9", list(stored))
    assert h["next_action"] is None
    assert next(s for s in h["steps"] if s["step"] == "acquisition")["state"] == "running"


def test_resume_mode_defaults_to_manual(monkeypatch):
    monkeypatch.delenv("DAS_RESUME_MODE", raising=False)
    assert hil_gateway.resume_mode() == "manual"
    monkeypatch.setenv("DAS_RESUME_MODE", "AUTO")
    assert hil_gateway.resume_mode() == "auto"


def test_login_roles_and_admin_check(monkeypatch):
    import importlib
    from fastapi import HTTPException
    monkeypatch.setenv("DAS_ADMIN_PASSWORD", "s3cret")
    from k9_dow.api import auth
    importlib.reload(auth)
    assert auth.login("demo", "demo")["role"] == "viewer"
    admin = auth.login("admin", "s3cret")
    assert admin["role"] == "admin" and auth.login("admin", "wrong") is None
    assert auth.require_admin("Bearer " + admin["token"])["u"] == "admin"
    for header, code in (("", 401), ("Bearer " + auth.login("demo", "demo")["token"], 403),
                         ("Bearer " + admin["token"][:-2] + "xx", 401)):
        with pytest.raises(HTTPException) as e:
            auth.require_admin(header)
        assert e.value.status_code == code
    monkeypatch.delenv("DAS_ADMIN_PASSWORD")
    importlib.reload(auth)
    assert auth.login("admin", "s3cret") is None          # no admin password = no admin


def test_advance_starts_next_stage_once(monkeypatch):
    import asyncio
    from fastapi import HTTPException
    from k9_dow.api import app as app_mod
    stored = {"jcids": {"status": "awaiting_gate"},
              "gate-JROC-VALIDATION": {"action": "complete", "actor": "a@k9x.ai", "decided_at": "t"}}
    monkeypatch.setattr(hil_gateway, "load_stage_result", lambda cfg, job, stage: stored.get(stage))
    monkeypatch.setattr(hil_gateway, "list_job_ids", lambda cfg: {"job-9": list(stored)})
    monkeypatch.setattr(hil_gateway, "save_stage_result",
                        lambda cfg, job, stage, res: stored.update({stage: res}))
    sent = []
    monkeypatch.setattr(app_mod, "_publish_to_router", sent.append)
    out = asyncio.run(app_mod.advance_job("job-9", admin={"u": "admin", "r": "admin"}))
    assert out["started"] == "acquisition" and out["approved_by"] == "a@k9x.ai"
    assert sent[0]["event_type"] == "gate_approved" and sent[0]["gate_id"] == "JROC-VALIDATION"
    assert sent[0]["decision"]["started_by"] == "admin" and "started-acquisition" in stored
    with pytest.raises(HTTPException) as e:                # already started
        asyncio.run(app_mod.advance_job("job-9", admin={"u": "admin", "r": "admin"}))
    assert e.value.status_code == 409


# ── Context enrichment inside the readiness and package squads ──

def _run_squad_with_fake_llm(monkeypatch, yaml_file, squad_id, payload):
    """Real SquadLoader + BaseSquad + DAS agents; only the model is faked."""
    from types import SimpleNamespace
    from k9_dow.orchestrators import acquisition_orchestrator as acq
    prompts = {}
    def fake(cfg, req):
        agent = req.metadata.get("agent", "?")
        prompts[agent] = req.prompt
        return SimpleNamespace(output=f"<{agent} output>")
    for mod in ("evidence_collector_agent", "readiness_scorer_agent", "gap_reporter_agent",
                "completeness_checker_agent", "package_builder_agent", "artifact_fetcher_agent"):
        m = __import__(f"k9_dow.agents.src.{mod}", fromlist=["x"])
        if hasattr(m, "llm_invoke"):
            monkeypatch.setattr(m, "llm_invoke", fake)
    orch = acq.AcquisitionOrchestrator(config={"emit_icd_docx": False})
    squad = orch._load_squad(yaml_file, squad_id)
    return squad.execute(payload), prompts


def test_gate_readiness_agents_build_on_each_other(monkeypatch):
    from k9_dow.gates.gate_registry import DAS_GATES
    crit = DAS_GATES["PATHWAY-MILESTONE"].entry_criteria
    result, prompts = _run_squad_with_fake_llm(monkeypatch, "gate_readiness_squad.yaml", "GateReadinessSquad",
        {"job_id": "j", "gate_id": "PATHWAY-MILESTONE", "gate_criteria": crit,
         "prior_outputs": {"criteria": {"criteria": []}, "icd": "prior-stage text"}})
    ev = next(p for a, p in prompts.items() if "Evidence" in a)
    sc = next(p for a, p in prompts.items() if "Scorer" in a or "Readiness" in a)
    gp = next(p for a, p in prompts.items() if "Gap" in a)
    assert "Funding line identified" in ev                       # loaded criteria, not the prior stage's empty list
    assert "Funding line identified" in sc and "Evidence Collector" in sc and "output>" in sc
    assert "Readiness Scorer" in gp and "output>" in gp


def test_package_agents_build_on_each_other(monkeypatch):
    result, prompts = _run_squad_with_fake_llm(monkeypatch, "package_assembly_squad.yaml", "PackageAssemblySquad",
        {"job_id": "j", "gate_id": "PATHWAY-MILESTONE", "prior_outputs": {"readiness_score": {"output": "45/100"}}})
    cc = next(p for a, p in prompts.items() if "Completeness" in a)
    pb = next(p for a, p in prompts.items() if "Builder" in a or "Package" in a)
    assert "Artifact Fetcher" in cc
    assert "Completeness Checker" in pb and "output>" in pb
