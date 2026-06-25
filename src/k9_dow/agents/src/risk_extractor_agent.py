# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations
import json
from k9_dow.agents.src.base_dow_agent import BaseDowAgent
from k9_dow.contracts.artifacts import DowAgentResult
from k9_dow.contracts.payloads import DowAgentPayload
from k9_dow.utils.markdown_utils import extract_first_json


class RiskExtractorAgent(BaseDowAgent):
    layer = "DoW RiskExtractor SBB"
    agent_name = "RiskExtractorAgent"

    def run_agent(self, payload: DowAgentPayload) -> DowAgentResult:
        prompt = self.build_prompt(
            role="Risk and Threat Analyst",
            task=(
                "Extract all risks, threats, vulnerabilities, and mitigation strategies.\n"
                "For each risk provide:\n"
                "- Risk name\n"
                "- Category (operational/technical/schedule/resource)\n"
                "- Description\n"
                "- Likelihood (high/medium/low — if stated)\n"
                "- Impact (high/medium/low — if stated)\n"
                "- Mitigation strategy (if stated)\n"
                "- Verbatim evidence from the source\n\n"
                "If not found: NOT PROVIDED IN SOURCE\n\n"
                "Return Markdown report and JSON:\n"
                '{"risks": [{"name": "...", "category": "...", "description": "...", '
                '"likelihood": "...", "impact": "...", "mitigation": "...", "evidence": "..."}]}'
            ),
            source_text=payload.source_markdown,
            prior_outputs="\n".join(payload.prior_outputs.values()) if payload.prior_outputs else "",
        )

        raw = self.invoke_llm(prompt)
        json_str = extract_first_json(raw)
        json_data = json.loads(json_str) if json_str else {"risks": []}
        citations = [
            r.get("evidence", "")
            for r in json_data.get("risks", [])
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
