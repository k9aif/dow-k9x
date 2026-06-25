# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations
from k9_dow.agents.src.base_dow_agent import BaseDowAgent
from k9_dow.contracts.artifacts import DowAgentResult
from k9_dow.contracts.payloads import DowAgentPayload


class ArchitectureAnalyzerAgent(BaseDowAgent):
    layer = "DoW ArchitectureAnalyzer SBB"
    agent_name = "ArchitectureAnalyzerAgent"

    def run_agent(self, payload: DowAgentPayload) -> DowAgentResult:
        prompt = self.build_prompt(
            role="DoD Architecture Fitness Analyst",
            task=(
                "Analyze the architecture against stated objectives and mission needs.\n\n"
                "Produce the following sections:\n"
                "## Objective Alignment\n"
                "For each objective, assess whether the architecture data supports it.\n"
                "Rate alignment: Strong / Partial / Weak / Not Addressed.\n\n"
                "## Architecture Gaps\n"
                "Identify gaps between objectives and architecture elements.\n\n"
                "## Fitness Assessment\n"
                "Overall fitness of the architecture for the stated mission context.\n\n"
                "## Recommendations\n"
                "Evidence-based recommendations to close gaps.\n\n"
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
