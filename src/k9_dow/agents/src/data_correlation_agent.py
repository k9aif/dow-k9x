# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations
from k9_dow.agents.src.base_dow_agent import BaseDowAgent
from k9_dow.contracts.artifacts import DowAgentResult
from k9_dow.contracts.payloads import DowAgentPayload


class DataCorrelationAgent(BaseDowAgent):
    layer = "DoW DataCorrelation SBB"
    agent_name = "DataCorrelationAgent"

    def run_agent(self, payload: DowAgentPayload) -> DowAgentResult:
        prompt = self.build_prompt(
            role="Architecture Data Correlation Specialist",
            task=(
                "Correlate all extracted architecture data across viewpoints.\n\n"
                "Produce the following sections:\n\n"
                "## Capability-to-Activity Traceability\n"
                "Cross-reference each capability with the operational activities it enables.\n"
                "Use a table: Capability | Operational Activity | Evidence.\n\n"
                "## System-to-Capability Mapping\n"
                "Map each system/service to the capabilities it supports.\n"
                "Use a table: System/Service | Capability | Relationship.\n\n"
                "## Mission-to-Architecture Traceability\n"
                "Trace from mission needs through capabilities to systems/services.\n"
                "Use a table: Mission Need | Capability | System/Service.\n\n"
                "## Evidence Map\n"
                "For each architecture element, list the source passages that support it.\n"
                "Flag elements with weak or missing evidence.\n\n"
                "## Taxonomy Alignment Issues\n"
                "Identify cases where the same concept appears under different names\n"
                "across viewpoints. Recommend canonical names.\n\n"
                "## Data Gaps\n"
                "List architecture elements referenced in one view but missing from others.\n"
                "Classify each gap by severity (critical/moderate/minor).\n\n"
                "If not found: NOT PROVIDED IN SOURCE"
            ),
            source_text=payload.source_markdown,
            prior_outputs="\n".join(payload.prior_outputs.values()) if payload.prior_outputs else "",
        )

        raw = self.invoke_llm(prompt)

        return DowAgentResult(
            job_id=payload.job_id,
            agent_name=self.agent_name,
            stage_id=payload.stage_id,
            status="completed",
            markdown=raw,
        )
