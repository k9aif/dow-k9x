# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations
from k9_dow.agents.src.base_dow_agent import BaseDowAgent
from k9_dow.contracts.artifacts import DowAgentResult
from k9_dow.contracts.payloads import DowAgentPayload


class VerificationAgent(BaseDowAgent):
    layer = "DoW Verification SBB"
    agent_name = "VerificationAgent"

    def run_agent(self, payload: DowAgentPayload) -> DowAgentResult:
        prompt = self.build_prompt(
            role="Architecture Verification Specialist",
            task=(
                "Perform cross-view consistency and completeness checks.\n\n"
                "Produce the following sections:\n\n"
                "## Cross-View Consistency\n"
                "Check that entities referenced in one viewpoint exist and are\n"
                "consistently named in related viewpoints.\n"
                "| Element | View A | View B | Status | Issue |\n"
                "Status: Consistent / Inconsistent / Missing.\n\n"
                "## Traceability Validation\n"
                "Verify complete traceability chains:\n"
                "- Mission Need -> Capability -> System/Service\n"
                "- Operational Activity -> System Function -> Service\n"
                "Flag broken chains.\n\n"
                "## Orphan Elements\n"
                "List architecture elements that appear in only one viewpoint\n"
                "with no cross-references.\n\n"
                "## Completeness Assessment\n"
                "For each viewpoint, assess data completeness:\n"
                "| Viewpoint | Elements Found | Completeness | Missing |\n\n"
                "## Consistency Scorecard\n"
                "Provide an overall consistency score (0-100) with rationale.\n\n"
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
