# SPDX-License-Identifier: Apache-2.0
# K9-AIF Framework
"""The DAS squad layer: squads are YAML, ``DasSquad`` runs each of them.

An orchestrator knows only squads (three-layer decoupling, k9_inspect K9-DEC-002).
It loads a squad by YAML file and squad id; the agents a squad needs are named in
that YAML and built here, never in an orchestrator. If a squad's agents change, no
orchestrator changes.

- ``DasSquad(BaseSquad)``: one class for every DAS squad, instantiated once per
  squad with that squad's agents. Its only DAS behaviour is ``before_step``: a
  withdrawn job (Jobs in Pipeline › Withdraw) stops before its next agent.
- ``squad_layer(config)``: the ``SquadLoader`` the entry point builds once and
  hands to every orchestrator as ``squads=``.

k9-aif >= 1.18.1 provides ``SquadLoader.from_agents`` and ``BaseSquad.before_step``.
Until DAS pins it, an older framework gets the same behaviour from the backport
below; with 1.18.1 installed the framework's own classes are used unchanged.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

import yaml

from k9_aif_abb.k9_squad.base_squad import BaseSquad
from k9_aif_abb.k9_squad.squad_loader import SquadLoader as _FrameworkSquadLoader

from k9_dow.utils.agent_loader import AgentLoader

AGENTS_DIR = Path(__file__).resolve().parent.parent / "agents" / "yaml"

_FRAMEWORK_CALLS_BEFORE_STEP = "before_step" in vars(BaseSquad)


class DasSquad(BaseSquad):
    """Every DAS squad. Agents and flow come from the squad's YAML."""

    def __init__(self, squad_id, agents, orchestrator=None, monitor=None):
        super().__init__(squad_id=squad_id, agents=agents, orchestrator=orchestrator, monitor=monitor)
        if not hasattr(self, "config"):
            self.config = {}
        if not _FRAMEWORK_CALLS_BEFORE_STEP:
            for agent in self.agents:          # k9-aif < 1.18.1: call before_step ourselves
                self._call_before_step(agent)

    def before_step(self, agent_name: str, context: dict) -> None:
        """A withdrawn job stops at its next agent. The agent's own execute, governance
        included, is unchanged."""
        from k9_dow.gates.hil_gateway import JobWithdrawn, withdrawn
        job_id = (context or {}).get("job_id")
        wd = withdrawn(self.config, job_id)
        if wd:
            raise JobWithdrawn(f"job {job_id} withdrawn by {wd.get('by')} at {wd.get('at')}")

    def _call_before_step(self, agent) -> None:
        run = agent.execute

        def execute(payload, _run=run, _name=agent.__class__.__name__):
            self.before_step(_name, payload)
            return _run(payload)
        agent.execute = execute


if hasattr(_FrameworkSquadLoader, "from_agents"):
    SquadLoader = _FrameworkSquadLoader
else:
    class SquadLoader(_FrameworkSquadLoader):
        """Backport of k9-aif 1.18.1's squad layer: builds the agents a squad YAML names."""

        def __init__(self, agent_loader, config=None, agent_kwargs=None, squad_cls=None):
            super().__init__(agent_registry=None)
            self.agent_loader = agent_loader
            self.config = config or {}
            self.agent_kwargs = dict(agent_kwargs or {})
            self.squad_cls = squad_cls or BaseSquad

        @classmethod
        def from_agents(cls, agents_dir, config=None, *, agent_kwargs=None, squad_cls=None, **_):
            return cls(AgentLoader(agents_dir), config=config, agent_kwargs=agent_kwargs, squad_cls=squad_cls)

        def load_one(self, path, squad_id: str, config: Optional[Dict[str, Any]] = None,
                     agent_kwargs: Optional[Dict[str, Any]] = None):
            path = Path(path)
            if not path.exists():
                raise FileNotFoundError(f"Squad config file not found: {path}")
            squads_cfg = (yaml.safe_load(path.read_text(encoding="utf-8")) or {}).get("squads") or {}
            if squad_id not in squads_cfg:
                raise KeyError(f"Squad '{squad_id}' not found in config. "
                               f"Available squads: {', '.join(sorted(squads_cfg)) or 'none'}")
            cfg = squads_cfg[squad_id]
            run_config = self.config if config is None else config
            kwargs = {**self.agent_kwargs, **(agent_kwargs or {})}
            names = cfg.get("agents") or []
            if not names:
                raise ValueError(f"Squad '{squad_id}' must define at least one agent")
            agents = []
            for name in names:
                try:
                    agent_cls = self.agent_loader.resolve_class(name)
                    agents.append(agent_cls(config=self.agent_loader.merge_with_global(name, run_config), **kwargs))
                except Exception as exc:
                    raise ValueError(f"Failed to create agent '{name}' for squad '{squad_id}': {exc}") from exc
            squad = self.squad_cls(squad_id=squad_id, agents=agents,
                                   monitor=self.monitor_cls() if self.monitor_cls else None)
            squad.config = run_config
            squad.description = cfg.get("description", "")
            squad.flow = cfg.get("flow", [])
            squad.metadata = cfg
            return squad


def squad_layer(config: Dict[str, Any]) -> SquadLoader:
    """The squad layer for every DAS orchestrator (built once, at the entry point)."""
    return SquadLoader.from_agents(AGENTS_DIR, config=config, squad_cls=DasSquad)
