# SPDX-License-Identifier: Apache-2.0
# DoW Architecture Workbench — AgentLoader is the framework's (k9-aif >= 1.15):
# agent classes resolve from each agent YAML's class + module, so orchestrators
# reference agents by name and never import them (three-layer decoupling).

from k9_aif_abb.k9_agents.agent_loader import AgentLoader

__all__ = ["AgentLoader"]
