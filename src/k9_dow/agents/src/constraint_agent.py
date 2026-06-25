# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations
import json
from k9_dow.agents.src.base_dow_agent import BaseDowAgent
from k9_dow.contracts.artifacts import DowAgentResult
from k9_dow.contracts.payloads import DowAgentPayload
from k9_dow.utils.markdown_utils import extract_first_json


class ConstraintAgent(BaseDowAgent):
    layer = "DoW Constraint SBB"
    agent_name = "ConstraintAgent"

    def run_agent(self, payload: DowAgentPayload) -> DowAgentResult:
        prompt = self.build_prompt(
            role="Architecture Constraint Analyst",
            task=(
                "Extract all constraints from the source document and build a constraint register.\n"
                "For each constraint provide:\n"
                "- Constraint description\n"
                "- Type (policy/regulatory/technical/resource/schedule/organizational)\n"
                "- Scope impact (which scope domains or boundaries are affected)\n"
                "- Verbatim evidence from the source\n\n"
                "If no constraints found, write: NOT PROVIDED IN SOURCE\n\n"
                "Return Markdown report and JSON:\n"
                '{"constraints": [{"description": "...", "type": "...", "scope_impact": "...", "evidence": "..."}]}'
            ),
            source_text=payload.source_markdown,
            prior_outputs="\n".join(payload.prior_outputs.values()) if payload.prior_outputs else "",
        )

        raw = self.invoke_llm(prompt)
        json_str = extract_first_json(raw)
        json_data = json.loads(json_str) if json_str else {"constraints": []}
        citations = [
            c.get("evidence", "")
            for c in json_data.get("constraints", [])
            if c.get("evidence")
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
