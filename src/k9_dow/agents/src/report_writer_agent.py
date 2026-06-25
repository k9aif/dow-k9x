# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations
from k9_dow.agents.src.base_dow_agent import BaseDowAgent
from k9_dow.contracts.artifacts import DowAgentResult
from k9_dow.contracts.payloads import DowAgentPayload


class ReportWriterAgent(BaseDowAgent):
    """
    Compiles final architecture reports from prior agent outputs.

    This is an assembly agent — it does NOT invoke the LLM.
    It organizes prior outputs into a structured document.
    """

    layer = "DoW ReportWriter SBB"
    agent_name = "ReportWriterAgent"

    def run_agent(self, payload: DowAgentPayload) -> DowAgentResult:
        if not payload.prior_outputs:
            return DowAgentResult(
                job_id=payload.job_id,
                agent_name=self.agent_name,
                stage_id=payload.stage_id,
                status="completed",
                markdown="## Architecture Report\n\nNo prior outputs to compile.\n",
            )

        sections = ["# Architecture Report\n"]
        sections.append(f"**Job:** {payload.job_id}  ")
        sections.append(f"**Stage:** {payload.stage_id}\n")
        sections.append("---\n")

        # Table of contents
        sections.append("## Table of Contents\n")
        for idx, agent_name in enumerate(payload.prior_outputs.keys(), 1):
            anchor = agent_name.lower().replace(" ", "-")
            sections.append(f"{idx}. [{agent_name}](#{anchor})")
        sections.append("")

        # Agent output sections
        for agent_name, output_text in payload.prior_outputs.items():
            sections.append(f"## {agent_name}\n")
            sections.append(output_text)
            sections.append("\n---\n")

        report = "\n".join(sections)
        artifact_paths = [f"{payload.job_id}/{payload.stage_id}/architecture_report.md"]

        return DowAgentResult(
            job_id=payload.job_id,
            agent_name=self.agent_name,
            stage_id=payload.stage_id,
            status="completed",
            markdown=report,
            json_data={"artifact_paths": artifact_paths},
        )
