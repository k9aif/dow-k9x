# SPDX-License-Identifier: Apache-2.0
# K9-AIF Framework
"""Policy mappings (config/mappings/*.yaml): policy kept as data, not in agent prompts."""

from pathlib import Path

import pytest
import yaml

import k9_dow
from k9_dow.config.policy_mappings import MAPPINGS_DIR, load_mapping, render_mapping

ROOT = Path(k9_dow.__file__).parent
SOURCES = yaml.safe_load((ROOT / "config" / "process_model.yaml").read_text())["process_model"]["sources"]


@pytest.mark.parametrize("path", sorted(MAPPINGS_DIR.glob("*.yaml")), ids=lambda p: p.stem)
def test_every_mapping_loads_and_cites_a_process_model_source(path):
    m = load_mapping(path.stem)
    assert m["source"] in SOURCES
    for entry in (m.get("tiers") or []) + [m.get("criteria") or {"cite": "x"}]:
        assert entry.get("cite"), entry
    assert render_mapping(path.stem)


def test_jsd_tiers_match_cjcsm_5123_01a_encl_b():
    """Encl. B 2.b(3)-(6): one ACAT level per tier. The 2026-10-09 prompt lumped ACAT I-III together."""
    tiers = {t["designator"]: t for t in load_mapping("jsd")["tiers"]}
    assert [t for t in tiers] == ["JROC Interest", "JCB Interest", "FCB Interest", "Service Information"]
    assert {d: t["acat"] for d, t in tiers.items()} == {
        "JROC Interest": "ACAT I", "JCB Interest": "ACAT II", "FCB Interest": "ACAT III", "Service Information": None}
    assert {d: t["cite"] for d, t in tiers.items()} == {
        "JROC Interest": "Encl. B 2.b(3)", "JCB Interest": "Encl. B 2.b(4)",
        "FCB Interest": "Encl. B 2.b(5)", "Service Information": "Encl. B 2.b(6)"}
    for d, t in tiers.items():
        if t["acat"]:
            assert t["condition"].count(f"{t['acat']} or equivalent") == 2
            other = {"ACAT I", "ACAT II", "ACAT III"} - {t["acat"]}
            assert not any(f"{o} or" in t["condition"] for o in other), d
    assert len(load_mapping("jsd")["criteria"]["items"]) == 5


def test_jsd_rules_forbid_inferring_acat_and_require_undetermined():
    rules = " ".join(load_mapping("jsd")["rules"])
    assert "JSD undetermined: ACAT needed" in rules
    assert "Never infer an ACAT" in rules
    assert "SOURCE INCONSISTENT WITH POLICY" in rules


def test_jsd_agent_prompt_carries_the_mapping_not_its_own_rules():
    from k9_dow.agents.src.package_writers import JsdRecommenderAgent
    from k9_dow.utils.agent_loader import AgentLoader
    loader = AgentLoader(ROOT / "agents" / "yaml")
    cfg = loader.merge_with_global("JsdRecommenderAgent", {})
    assert cfg.get("mappings") == ["jsd"]
    assert "ACAT I" not in " ".join(cfg.get("instructions") or [])    # tier levels live in the mapping only
    prompt = JsdRecommenderAgent(config=cfg).build_prompt({"source_markdown": "# Requirement", "prior_outputs": {}})
    assert "| JROC Interest | ACAT I |" in prompt and "| FCB Interest | ACAT III |" in prompt
    assert "CJCSM 5123.01A Encl. B 2.b(5)" in prompt


def test_unknown_mapping_fails_loudly():
    with pytest.raises(FileNotFoundError):
        load_mapping("no_such_mapping")
