# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations
import json
from k9_dow.agents.src.base_dow_agent import BaseDowAgent
from k9_dow.contracts.artifacts import DowAgentResult
from k9_dow.contracts.payloads import DowAgentPayload
from k9_dow.utils.markdown_utils import extract_first_json


class StakeholderExtractorAgent(BaseDowAgent):
    layer = "DoW StakeholderExtractor SBB"
    agent_name = "StakeholderExtractorAgent"

    def run_agent(self, payload: DowAgentPayload) -> DowAgentResult:
        prompt = self.build_prompt(
            role="Stakeholder Identification Specialist",
            task=(
                "Extract all stakeholders from the source document.\n"
                "For each stakeholder provide:\n"
                "- Name or title\n"
                "- Role/responsibility\n"
                "- Organization (if stated)\n"
                "- Verbatim evidence snippet from source\n\n"
                "If no stakeholders are found, write: NOT PROVIDED IN SOURCE\n\n"
                "Return Markdown with a table and also JSON:\n"
                '{"stakeholders": [{"name": "...", "role": "...", "org": "...", "evidence": "..."}]}'
            ),
            source_text=payload.source_markdown,
            prior_outputs="\n".join(payload.prior_outputs.values()) if payload.prior_outputs else "",
        )

        raw = self.invoke_llm(prompt)
        json_str = extract_first_json(raw)
        json_data = json.loads(json_str) if json_str else {"stakeholders": []}

        citations = [s.get("evidence", "") for s in json_data.get("stakeholders", []) if s.get("evidence")]

        return DowAgentResult(
            job_id=payload.job_id,
            agent_name=self.agent_name,
            stage_id=payload.stage_id,
            status="completed",
            markdown=raw,
            json_data=json_data,
            citations=citations,
        )
