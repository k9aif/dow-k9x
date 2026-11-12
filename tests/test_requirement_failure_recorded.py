# SPDX-License-Identifier: Apache-2.0
"""A failed requirement stage is recorded with its reason (v1.3.7), so the job's record and Jobs in
Pipeline show it. Found on JOB-20261112-C14FF7: the stage failed, the job queue said "error", and the
record still showed the requirement stage as not reached."""
import pytest

from k9_dow.gates import hil_gateway
from k9_dow.orchestrators.requirement_orchestrator import RequirementOrchestrator


def test_requirement_failure_is_stored_and_reraised(monkeypatch):
    saved = {}
    monkeypatch.setattr(hil_gateway, "save_stage_result", lambda cfg, job, run, rec: saved.update({run: rec}) or "uri")
    orch = RequirementOrchestrator.__new__(RequirementOrchestrator)
    orch.config, orch.layer = {}, "DAS RequirementOrchestrator"
    orch._classification = orch._shield = orch._governance = None
    orch._emit = lambda *a, **k: None
    orch._screen_document = lambda job_id, filename, payload: {}
    orch._load_squad = lambda *a: None
    def boom(*a, **k):
        raise RuntimeError('extension "vector" is not available')
    orch._run_squad = boom
    with pytest.raises(RuntimeError):
        orch.execute_flow({"job_id": "JOB-T", "filename": "x.md", "document_type": "capability_gap"})
    rec = saved["requirement"]
    assert rec["status"] == "error" and "vector" in rec["detail"]

