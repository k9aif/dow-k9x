# SPDX-License-Identifier: Apache-2.0
# DoW Architecture Workbench — AgentLoader (same pattern as EOC)

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

log = logging.getLogger(__name__)


class AgentLoader:
    """
    Loads per-agent YAML files from agents/yaml/ and provides merged configs.

    Merge strategy: global config supplies infrastructure (inference, messaging,
    postgres, etc.); agent YAML supplies behavior (role, goal, instructions,
    model, pattern, etc.). Agent YAML wins on key collision.
    """

    def __init__(self, yaml_dir: str | Path) -> None:
        self.yaml_dir = Path(yaml_dir)
        self._by_class: Dict[str, Dict[str, Any]] = {}
        self._load_all()

    def _load_all(self) -> None:
        if not self.yaml_dir.exists():
            log.warning("AgentLoader: yaml_dir not found: %s", self.yaml_dir)
            return
        for path in sorted(self.yaml_dir.glob("*.yaml")):
            try:
                with path.open("r", encoding="utf-8") as fh:
                    data = yaml.safe_load(fh) or {}
                class_name = (data.get("class") or "").strip()
                if class_name:
                    self._by_class[class_name] = data
                    log.debug("AgentLoader: indexed %s from %s", class_name, path.name)
            except Exception as exc:
                log.warning("AgentLoader: could not load %s: %s", path, exc)

    def get_agent_yaml(self, class_name: str) -> Optional[Dict[str, Any]]:
        return self._by_class.get(class_name)

    def merge_with_global(self, class_name: str, global_config: Dict[str, Any]) -> Dict[str, Any]:
        agent_yaml = self._by_class.get(class_name, {})
        return {**global_config, **agent_yaml}

    def has_agent(self, class_name: str) -> bool:
        return class_name in self._by_class

    def list_classes(self) -> List[str]:
        return list(self._by_class.keys())
