# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations
from k9_dow.agents.src.base_dow_agent import BaseDowAgent
from k9_dow.contracts.artifacts import DowAgentResult
from k9_dow.contracts.payloads import DowAgentPayload


class PresentationAgent(BaseDowAgent):
    layer = "DoW Presentation SBB"
    agent_name = "PresentationAgent"

    def run_agent(self, payload: DowAgentPayload) -> DowAgentResult:
        prompt = self.build_prompt(
            role="Senior Architecture Presentation Specialist",
            task=(
                "Build a decision-ready presentation package from all prior outputs.\n\n"
                "Use this executive briefing format:\n\n"
                "# Architecture Decision Package\n\n"
                "## 1. Executive Summary\n"
                "Two-paragraph overview: what was analyzed, key conclusions.\n\n"
                "## 2. Mission Context and Objectives\n"
                "Restate the mission context and architecture objectives.\n\n"
                "## 3. Key Findings\n"
                "Organize by domain:\n"
                "### Capability Findings\n"
                "### Operational Findings\n"
                "### System/Service Findings\n"
                "### Risk Findings\n\n"
                "## 4. Gap Analysis Summary\n"
                "Consolidated view of all identified gaps, ordered by severity.\n\n"
                "## 5. Architecture Decision Matrix\n"
                "| Decision Area | Options | Recommendation | Rationale |\n\n"
                "## 6. Action Items (Top 10)\n"
                "Prioritized list of the most critical action items.\n\n"
                "## 7. Readiness Assessment\n"
                "Overall architecture readiness: Ready / Conditionally Ready / Not Ready.\n"
                "Justify with evidence from prior outputs.\n\n"
                "## 8. Next Steps\n"
                "Recommended next steps for the architecture development effort.\n\n"
                "IMPORTANT: Do NOT add new analysis. Compile and organize only.\n"
                "Reference evidence from prior outputs.\n\n"
                "If not found: NOT PROVIDED IN SOURCE"
            ),
            source_text=payload.source_markdown[:1000],
            prior_outputs="\n".join(payload.prior_outputs.values()) if payload.prior_outputs else "",
        )

        raw = self.invoke_llm(prompt, task_type="general")

        return DowAgentResult(
            job_id=payload.job_id,
            agent_name=self.agent_name,
            stage_id=payload.stage_id,
            status="completed",
            markdown=raw,
        )
