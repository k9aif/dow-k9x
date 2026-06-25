# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations
import json
from k9_dow.agents.src.base_dow_agent import BaseDowAgent
from k9_dow.contracts.artifacts import DowAgentResult
from k9_dow.contracts.payloads import DowAgentPayload
from k9_dow.utils.markdown_utils import extract_first_json


class RequirementAgent(BaseDowAgent):
    layer = "DoW Requirement SBB"
    agent_name = "RequirementAgent"

    def run_agent(self, payload: DowAgentPayload) -> DowAgentResult:
        prompt = self.build_prompt(
            role="Requirements Engineer",
            task=(
                "Extract and structure requirements from the analysis outputs.\n"
                "For each requirement provide:\n"
                "- Requirement ID (REQ-NNN)\n"
                "- Statement\n"
                "- Type (functional/non-functional/interface/performance)\n"
                "- Priority (critical/high/medium/low)\n"
                "- Traces to (which objective, capability, or gap)\n"
                "- Verbatim evidence or rationale\n\n"
                "If not found: NOT PROVIDED IN SOURCE\n\n"
                "Return Markdown report and JSON:\n"
                '{"requirements": [{"id": "REQ-001", "statement": "...", '
                '"type": "...", "priority": "...", "traces_to": "...", "evidence": "..."}]}'
            ),
            source_text=payload.source_markdown,
            prior_outputs="\n".join(payload.prior_outputs.values()) if payload.prior_outputs else "",
        )

        raw = self.invoke_llm(prompt)
        json_str = extract_first_json(raw)
        json_data = json.loads(json_str) if json_str else {"requirements": []}
        citations = [
            r.get("evidence", "")
            for r in json_data.get("requirements", [])
            if r.get("evidence")
        ]

        return DowAgentResult(
            job_id=payload.job_id,
            agent_name=self.agent_name,
            stage_id=payload.stage_id,
            status="completed",
            markdown=raw,
            json_data=json_data,
            citations=citations,
        )
