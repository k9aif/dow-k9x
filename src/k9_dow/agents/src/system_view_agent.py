# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations
from k9_dow.agents.src.base_dow_agent import BaseDowAgent
from k9_dow.contracts.artifacts import DowAgentResult
from k9_dow.contracts.payloads import DowAgentPayload


class SystemViewAgent(BaseDowAgent):
    layer = "DoW SystemView SBB"
    agent_name = "SystemViewAgent"

    def run_agent(self, payload: DowAgentPayload) -> DowAgentResult:
        prompt = self.build_prompt(
            role="System Architecture View Specialist",
            task=(
                "Structure system-level architecture views from the extracted data.\n\n"
                "Produce the following sections:\n"
                "## SV-1 — System Interface Description\n"
                "List each system, its interfaces, and connected systems.\n"
                "Use a table: System | Interface | Connected To | Protocol.\n\n"
                "## SV-2 — System Resource Flow\n"
                "Map resource flows between systems.\n"
                "Use a table: Source System | Resource | Destination System.\n\n"
                "## SV-4 — System Functionality\n"
                "Map system functions to the systems that perform them.\n"
                "Use a table: System | Function | Description.\n\n"
                "Cross-reference with operational activities from prior outputs.\n"
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
