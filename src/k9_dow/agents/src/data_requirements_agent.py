# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations
import json
from k9_dow.agents.src.base_dow_agent import BaseDowAgent
from k9_dow.contracts.artifacts import DowAgentResult
from k9_dow.contracts.payloads import DowAgentPayload
from k9_dow.utils.markdown_utils import extract_first_json


class DataRequirementsAgent(BaseDowAgent):
    layer = "DoW DataRequirements SBB"
    agent_name = "DataRequirementsAgent"

    def run_agent(self, payload: DowAgentPayload) -> DowAgentResult:
        prompt = self.build_prompt(
            role="Architecture Data Requirements Analyst",
            task=(
                "Identify the required architecture data from the source document "
                "and prior stage outputs.\n"
                "For each data requirement provide:\n"
                "- Data element name\n"
                "- Description\n"
                "- DoDAF view mapping (which DoDAF view this data supports: "
                "OV-1, OV-2, OV-5, SV-1, SV-4, CV-2, etc.)\n"
                "- Data source (where this data originates or should be collected)\n"
                "- Priority (critical/important/nice-to-have)\n"
                "- Verbatim evidence from the source\n\n"
                "If not found: NOT PROVIDED IN SOURCE\n\n"
                "Return Markdown report and JSON:\n"
                '{"data_requirements": [{"name": "...", "description": "...", '
                '"view_mapping": ["..."], "data_source": "...", "priority": "...", '
                '"evidence": "..."}]}'
            ),
            source_text=payload.source_markdown,
            prior_outputs="\n".join(payload.prior_outputs.values()) if payload.prior_outputs else "",
        )

        raw = self.invoke_llm(prompt)
        json_str = extract_first_json(raw)
        json_data = json.loads(json_str) if json_str else {"data_requirements": []}
        citations = [
            d.get("evidence", "")
            for d in json_data.get("data_requirements", [])
            if d.get("evidence")
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
