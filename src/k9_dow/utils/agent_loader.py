# SPDX-License-Identifier: Apache-2.0
# DoW Architecture Workbench — AgentLoader is the framework's: agent classes resolve from each
# agent YAML's class + module, so orchestrators reference agents by name and never import them
# (three-layer decoupling).
#
# k9-aif >= 1.15 provides AgentLoader.resolve_class. Until DAS pins 1.15, an older framework gets
# the same method here; with 1.15 installed the framework's own class is used unchanged.

import importlib

from k9_aif_abb.k9_agents.agent_loader import AgentLoader as _FrameworkAgentLoader

if hasattr(_FrameworkAgentLoader, "resolve_class"):
    AgentLoader = _FrameworkAgentLoader
else:
    class AgentLoader(_FrameworkAgentLoader):
        def resolve_class(self, class_name: str) -> type:
            """The agent class named in YAML, imported from its ``module:`` field (as in k9-aif 1.15)."""
            spec = self._by_class.get(class_name)
            if not spec:
                raise KeyError(f"AgentLoader: no agent YAML with class: {class_name} in {self.yaml_dir}")
            module = (spec.get("module") or "").strip()
            if not module:
                raise KeyError(f"AgentLoader: agent YAML for {class_name} has no 'module:' field")
            cls = getattr(importlib.import_module(module), class_name, None)
            if cls is None:
                raise ImportError(f"AgentLoader: {module} has no class {class_name}")
            return cls

__all__ = ["AgentLoader"]
