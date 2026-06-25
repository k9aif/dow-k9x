# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations
from k9_dow.agents.src.base_dow_agent import BaseDowAgent
from k9_dow.contracts.artifacts import DowAgentResult
from k9_dow.contracts.payloads import DowAgentPayload


class MissionAssessmentAgent(BaseDowAgent):
    layer = "DoW MissionAssessment SBB"
    agent_name = "MissionAssessmentAgent"

    def run_agent(self, payload: DowAgentPayload) -> DowAgentResult:
        prompt = self.build_prompt(
            role="Mission Context Analyst",
            task=(
                "Assess the mission context from the source document:\n"
                "1. Mission context summary\n"
                "2. Operational environment description\n"
                "3. Mission threads or operational threads (if present)\n"
                "4. Operational relevance assessment\n\n"
                "Cite evidence for all claims.\n"
                "If no mission context found, write: NOT PROVIDED IN SOURCE"
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
