# SPDX-License-Identifier: Apache-2.0
"""The gate registry reads the current process's gates from config/process_model.yaml."""

from k9_dow.config.process_model import load_process_model
from k9_dow.gates.gate_registry import DAS_GATES, PROCESS_GATES, GateRegistry
from k9_dow.graph.schema import GateType


def test_every_process_gate_is_registered_from_the_file():
    pm = load_process_model()
    assert set(PROCESS_GATES) == set(pm.gates)
    for gid, g in pm.gates.items():
        d = DAS_GATES[gid]
        assert d.entry_criteria == g.entry_criteria
        assert d.sources == g.sources and d.authority == g.authority
        assert d.process_model == pm.id and d.non_delegable


def test_jci_review_never_blocks():
    assert DAS_GATES["JCI-REVIEW"].blocking is False
    assert all(DAS_GATES[g].blocking for g in ("SERVICE-VALIDATION", "MDD", "MILESTONE-A", "SE-REVIEW-SRR"))


def test_srr_is_the_process_definition():
    srr = DAS_GATES["SE-REVIEW-SRR"]
    assert srr.type == GateType.REVIEW_APPROVE and srr.owning_orchestrator == "tmrr"
    assert any("measurable and testable" in c for c in srr.entry_criteria)


def test_equal_weights_for_process_gates():
    from k9_dow.gates.readiness import weights_for
    n = len(DAS_GATES["MILESTONE-A"].entry_criteria)
    assert weights_for("MILESTONE-A", n) == [1] * n


def test_decision_needs_a_named_person():
    from k9_dow.gates.gate_model import GateDecision
    from k9_dow.graph.schema import GateAction
    import pytest
    reg = GateRegistry()
    reg.init_gate("MDD")
    with pytest.raises(ValueError):
        reg.record_decision("MDD", GateDecision(gate_id="MDD", action=GateAction.APPROVE, decided_by="", rationale=""))
