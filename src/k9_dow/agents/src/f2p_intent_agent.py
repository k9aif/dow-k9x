# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations
from k9_dow.agents.src.base_dow_agent import BaseDowAgent
from k9_dow.contracts.artifacts import DowAgentResult
from k9_dow.contracts.payloads import DowAgentPayload


class F2PIntentAgent(BaseDowAgent):
    layer = "DoW F2PIntent SBB"
    agent_name = "F2PIntentAgent"

    def run_agent(self, payload: DowAgentPayload) -> DowAgentResult:
        prior = "\n\n---\n\n".join(
            f"### {name}\n{text}" for name, text in payload.prior_outputs.items()
        ) if payload.prior_outputs else "No prior outputs available."

        prompt = self.build_prompt(
            role="Fit-for-Purpose Intent Analyst",
            task=(
                "Based on the prior agent outputs below, create a Fit-for-Purpose "
                "intent statement that synthesizes:\n"
                "1. Key stakeholders and their concerns\n"
                "2. Core pain points and operational problems\n"
                "3. Stated objectives and desired outcomes\n"
                "4. Mission context and relevance\n\n"
                "Then provide a readiness assessment:\n"
                "- READY: sufficient for full architecture development\n"
                "- NEEDS_ENRICHMENT: viable but needs additional context\n"
                "- INSUFFICIENT: not enough information for architecture work\n\n"
                "Use only information from prior outputs. Do not invent."
            ),
            source_text=payload.source_markdown[:2000],
            prior_outputs=prior,
        )

        raw = self.invoke_llm(prompt)

        return DowAgentResult(
            job_id=payload.job_id,
            agent_name=self.agent_name,
            stage_id=payload.stage_id,
            status="completed",
            markdown=raw,
        )
