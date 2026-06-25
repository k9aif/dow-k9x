# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations
import json
from k9_dow.agents.src.base_dow_agent import BaseDowAgent
from k9_dow.contracts.artifacts import DowAgentResult
from k9_dow.contracts.payloads import DowAgentPayload
from k9_dow.utils.markdown_utils import extract_first_json


class PainPointExtractorAgent(BaseDowAgent):
    layer = "DoW PainPointExtractor SBB"
    agent_name = "PainPointExtractorAgent"

    def run_agent(self, payload: DowAgentPayload) -> DowAgentResult:
        prompt = self.build_prompt(
            role="Pain Point and Operational Problem Analyst",
            task=(
                "Extract all pain points, challenges, and operational problems.\n"
                "For each provide:\n"
                "- Description\n"
                "- Category (operational/technical/organizational/resource)\n"
                "- Impact\n"
                "- Verbatim evidence\n\n"
                "Then write an OV-1 style problem framing paragraph.\n\n"
                "If no pain points found, write: NOT PROVIDED IN SOURCE\n\n"
                "Return Markdown report and JSON:\n"
                '{"pain_points": [{"description": "...", "category": "...", "impact": "...", "evidence": "..."}], '
                '"problem_framing": "..."}'
            ),
            source_text=payload.source_markdown,
            prior_outputs="\n".join(payload.prior_outputs.values()) if payload.prior_outputs else "",
        )

        raw = self.invoke_llm(prompt)
        json_str = extract_first_json(raw)
        json_data = json.loads(json_str) if json_str else {"pain_points": []}
        citations = [p.get("evidence", "") for p in json_data.get("pain_points", []) if p.get("evidence")]

        return DowAgentResult(
            job_id=payload.job_id,
            agent_name=self.agent_name,
            stage_id=payload.stage_id,
            status="completed",
            markdown=raw,
            json_data=json_data,
            citations=citations,
        )
