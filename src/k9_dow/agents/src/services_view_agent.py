# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations
from k9_dow.agents.src.base_dow_agent import BaseDowAgent
from k9_dow.contracts.artifacts import DowAgentResult
from k9_dow.contracts.payloads import DowAgentPayload


class ServicesViewAgent(BaseDowAgent):
    layer = "DoW ServicesView SBB"
    agent_name = "ServicesViewAgent"

    def run_agent(self, payload: DowAgentPayload) -> DowAgentResult:
        prompt = self.build_prompt(
            role="Service Architecture View Specialist",
            task=(
                "Structure service-level architecture views from the extracted data.\n\n"
                "Produce the following sections:\n"
                "## SvcV-1 — Service Context\n"
                "Describe service dependencies and interactions.\n"
                "Use a table: Service | Provider | Consumer | Interface | Protocol.\n\n"
                "## SvcV-3a — System-Service Matrix\n"
                "Map which systems host or provide which services.\n"
                "Use a table: System | Service | Relationship (hosts/consumes/provides).\n\n"
                "## SvcV-4 — Service Functionality\n"
                "Map service functions and their descriptions.\n"
                "Use a table: Service | Function | Description | Input | Output.\n\n"
                "## Service Dependency Chain\n"
                "Identify critical service dependency chains and single points of failure.\n\n"
                "Cross-reference with system views and operational activities from prior outputs.\n"
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
