# SPDX-License-Identifier: Apache-2.0
"""The process model file: current, sourced, ordered, and JCI never blocks."""

import copy
from pathlib import Path

import pytest
import yaml

from k9_dow.config.process_model import (
    PROCESS_MODEL_PATH,
    ProcessModelError,
    load_process_model,
    parse_process_model,
)

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def pm():
    return load_process_model()


@pytest.fixture
def raw():
    with open(PROCESS_MODEL_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


def test_version(pm):
    assert pm.id == "mca-2026-10"
    assert pm.as_of == "2026-10-09"
    assert pm.pathway == "major_capability_acquisition"


def test_main_line_order(pm):
    assert [s.id for s in pm.sequence()] == [
        "NORMALIZE", "SCREEN", "REQUIREMENT", "SERVICE-VALIDATION", "MDD-PACKAGE", "MDD", "MSA",
        "MILESTONE-A-PACKAGE", "MILESTONE-A", "TMRR-SRR", "SE-REVIEW-SRR",
    ]


def test_gates(pm):
    assert set(pm.gates) == {"SERVICE-VALIDATION", "JCI-REVIEW", "MDD", "MILESTONE-A", "SE-REVIEW-SRR"}
    assert pm.blocking_gates() == ["SERVICE-VALIDATION", "MDD", "MILESTONE-A", "SE-REVIEW-SRR"]


def test_jci_runs_in_parallel_and_never_blocks(pm):
    assert pm.stage("JCI-REVIEW").parallel
    assert not pm.gate("JCI-REVIEW").blocking
    assert "JCI-REVIEW" not in [s.id for s in pm.sequence()]
    # Service validation leads on to the MDD package, not to the joint review.
    assert pm.next_stage("SERVICE-VALIDATION").id == "MDD-PACKAGE"


def test_srr_follows_milestone_a(pm):
    seq = [s.id for s in pm.sequence()]
    assert seq.index("MSA") < seq.index("MILESTONE-A") < seq.index("SE-REVIEW-SRR")


def test_no_jcids_era_names(pm):
    names = [s.id for s in pm.stages] + list(pm.gates)
    for old in ("JROC-VALIDATION", "PATHWAY-MILESTONE", "JCIDS"):
        assert old not in names


def test_every_citation_names_a_listed_source(pm):
    for s in pm.stages:
        for c in s.sources:
            assert c.split()[0] in pm.sources
    for g in pm.gates.values():
        assert g.sources and g.entry_criteria


def test_source_files_present(pm):
    for key, src in pm.sources.items():
        assert (ROOT / src["file"]).exists(), f"{key}: {src['file']} missing"


def test_rejects_a_blocking_parallel_gate(raw):
    bad = copy.deepcopy(raw)
    bad["process_model"]["gates"]["JCI-REVIEW"]["blocking"] = True
    with pytest.raises(ProcessModelError):
        parse_process_model(bad)


def test_rejects_an_unknown_source(raw):
    bad = copy.deepcopy(raw)
    bad["process_model"]["gates"]["MDD"]["sources"] = ["S9 1.1"]
    with pytest.raises(ProcessModelError):
        parse_process_model(bad)


def test_rejects_an_unsourced_stage(raw):
    bad = copy.deepcopy(raw)
    bad["process_model"]["stages"][2]["sources"] = []
    with pytest.raises(ProcessModelError):
        parse_process_model(bad)


def test_owners(pm):
    assert {s.owner for s in pm.stages} == {"intake", "requirement", "msa", "tmrr"}
    assert pm.gate("SERVICE-VALIDATION").owner == "requirement"
    assert pm.gate("MILESTONE-A").owner == "msa"
    assert pm.gate("SE-REVIEW-SRR").type == "REVIEW_APPROVE"
    assert pm.gate("MDD").type == "PREPARE_DECIDE"


def test_rejects_an_unknown_owner(raw):
    bad = copy.deepcopy(raw)
    bad["process_model"]["stages"][2]["owner"] = "jcids"
    with pytest.raises(ProcessModelError):
        parse_process_model(bad)
