# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations
from k9_dow.agents.src.base_dow_agent import BaseDowAgent
from k9_dow.contracts.artifacts import DowAgentResult
from k9_dow.contracts.payloads import DowAgentPayload


class SummarizerAgent(BaseDowAgent):
    layer = "DoW Summarizer SBB"
    agent_name = "SummarizerAgent"

    def run_agent(self, payload: DowAgentPayload) -> DowAgentResult:
        prior = "\n\n---\n\n".join(
            f"### {name}\n{text}" for name, text in payload.prior_outputs.items()
        ) if payload.prior_outputs else "No prior outputs."

        prompt = self.build_prompt(
            role="Technical Report Writer",
            task=(
                "Compile the following agent outputs into a structured stage report.\n\n"
                "Use this format:\n"
                "# Stage Report\n"
                "## Source Summary\n"
                "## Extracted Findings\n"
                "## Analysis\n"
                "## Evidence / Citations\n"
                "## Unsupported or Missing Information\n"
                "## Next Steps\n\n"
                "Do not add new analysis — only compile and organize.\n"
                "Preserve all citations."
            ),
            source_text=payload.source_markdown[:1000],
            prior_outputs=prior,
        )

        raw = self.invoke_llm(prompt, task_type="general")

        return DowAgentResult(
            job_id=payload.job_id,
            agent_name=self.agent_name,
            stage_id=payload.stage_id,
            status="completed",
            markdown=raw,
        )
