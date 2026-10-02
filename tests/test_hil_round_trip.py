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


def test_se_is_a_labelled_demonstration_endpoint():
    from k9_dow.orchestrators.se_orchestrator import SeOrchestrator
    events = []
    result = SeOrchestrator(config={}, progress_callback=events.append).execute_flow(
        gate_approved_event("PATHWAY-MILESTONE", hil_reply("job-7", actor="mda@k9x.ai")))
    assert result["status"] == "pipeline_complete" and result["demo_stub"] is True
    assert result["target_review"] == "SE-REVIEW-SRR"
    assert result["milestone_decision"]["actor"] == "mda@k9x.ai"
    assert [e["type"] for e in events] == ["OrchestratorStarted", "OrchestratorCompleted"]
