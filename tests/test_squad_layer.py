# SPDX-License-Identifier: Apache-2.0
# K9-AIF Framework
"""An orchestrator knows only squads (three-layer decoupling, k9_inspect K9-DEC-002).

The squad layer builds every agent a squad YAML names; no orchestrator lists agents.
If a squad's agents change, only its YAML (and the agent's own YAML and class) change.
"""

import ast
import re
from pathlib import Path

import pytest
import yaml

from k9_dow.squads.das_squad import DasSquad, squad_layer

SRC = Path(__file__).resolve().parent.parent / "src" / "k9_dow"
SQUAD_FILES = sorted((SRC / "squads" / "yaml").glob("*.yaml"))


@pytest.mark.parametrize("path", SQUAD_FILES, ids=lambda p: p.name)
def test_every_squad_builds_from_its_yaml(path):
    squads = squad_layer({})
    for squad_id, cfg in yaml.safe_load(path.read_text())["squads"].items():
        squad = squads.load_one(path, squad_id)
        assert isinstance(squad, DasSquad)
        assert [a.__class__.__name__ for a in squad.agents] == cfg["agents"]


def test_no_orchestrator_names_or_builds_agents():
    agent_names = set()
    for p in (SRC / "agents" / "yaml").glob("*.yaml"):
        agent_names.add((yaml.safe_load(p.read_text()) or {}).get("class"))
    offenders = []
    for p in (SRC / "orchestrators").glob("*.py"):
        tree = ast.parse(p.read_text())
        for n in ast.walk(tree):
            if isinstance(n, ast.Constant) and isinstance(n.value, str) and n.value in agent_names:
                offenders.append(f"{p.name}:{n.lineno} names {n.value}")
            name = n.id if isinstance(n, ast.Name) else n.attr if isinstance(n, ast.Attribute) else ""
            if name in ("AgentRegistry", "AgentLoader", "register_into"):
                offenders.append(f"{p.name}:{n.lineno} builds agents ({name})")
            if isinstance(n, ast.ImportFrom) and any(a.name in ("AgentRegistry", "AgentLoader") for a in n.names):
                offenders.append(f"{p.name}:{n.lineno} imports {[a.name for a in n.names]}")
    assert not offenders, offenders
