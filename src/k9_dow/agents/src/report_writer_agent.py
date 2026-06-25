# SPDX-License-Identifier: Apache-2.0
# DoW Architecture Workbench — ReportWriterAgent (SBB)
#
# Assembly agent — does NOT invoke the LLM.
# Organizes prior outputs into a structured document.

from typing import Any, Dict, Optional

from k9_aif_abb.k9_core.agent.base_agent import BaseAgent


class ReportWriterAgent(BaseAgent):
    layer = "DoW ReportWriter SBB"

    def __init__(self, config: Optional[Dict[str, Any]] = None, monitor=None, **kwargs):
        super().__init__(config or {}, monitor=monitor, **kwargs)

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        prior = payload.get("prior_outputs") or {}
        job_id = payload.get("job_id", "unknown")
        stage_id = payload.get("stage_id", "unknown")

        if not prior:
            self.publish_event({"type": "AgentCompleted", "agent": "ReportWriterAgent"})
            return {
                "agent": "ReportWriterAgent",
                "output": "## Architecture Report\n\nNo prior outputs to compile.\n",
            }

        sections = ["# Architecture Report\n"]
        sections.append(f"**Job:** {job_id}  ")
        sections.append(f"**Stage:** {stage_id}\n")
        sections.append("---\n")

        # Table of contents
        sections.append("## Table of Contents\n")
        for idx, agent_name in enumerate(prior.keys(), 1):
            anchor = agent_name.lower().replace(" ", "-")
            sections.append(f"{idx}. [{agent_name}](#{anchor})")
        sections.append("")

        # Agent output sections
        for agent_name, output_text in prior.items():
            sections.append(f"## {agent_name}\n")
            sections.append(output_text)
            sections.append("\n---\n")

        report = "\n".join(sections)

        self.publish_event({"type": "AgentCompleted", "agent": "ReportWriterAgent"})
        return {
            "agent": "ReportWriterAgent",
            "output": report,
        }
