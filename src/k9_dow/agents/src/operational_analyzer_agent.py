# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations
from k9_dow.agents.src.base_dow_agent import BaseDowAgent
from k9_dow.contracts.artifacts import DowAgentResult
from k9_dow.contracts.payloads import DowAgentPayload


class OperationalAnalyzerAgent(BaseDowAgent):
    layer = "DoW OperationalAnalyzer SBB"
    agent_name = "OperationalAnalyzerAgent"

    def run_agent(self, payload: DowAgentPayload) -> DowAgentResult:
        prompt = self.build_prompt(
            role="Operational Architecture Analyst",
            task=(
                "Analyze the operational architecture for mission alignment.\n\n"
                "Produce the following sections:\n\n"
                "## Mission Alignment Assessment\n"
                "For each operational activity, assess alignment to the stated mission.\n"
                "| Activity | Mission Need | Alignment | Evidence |\n"
                "Alignment: Direct / Indirect / Not Aligned / Unclear.\n\n"
                "## Operational Strengths\n"
                "List well-supported operational areas with strong evidence:\n"
                "- Clear performer assignments\n"
                "- Well-defined information exchanges\n"
                "- Complete activity decompositions\n\n"
                "## Operational Weaknesses\n"
                "List operational areas with deficiencies:\n"
                "- Activities without assigned performers\n"
                "- Missing or undefined information exchanges\n"
                "- Incomplete process flows\n\n"
                "## Operational Gaps\n"
                "Identify missing operational elements:\n"
                "- Mission needs without supporting activities\n"
                "- Activities without supporting systems\n"
                "- Disconnected operational nodes\n\n"
                "## Operational Risk Summary\n"
                "Summarize key operational risks based on the analysis.\n\n"
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
