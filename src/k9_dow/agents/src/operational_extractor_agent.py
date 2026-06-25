# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations
import json
from k9_dow.agents.src.base_dow_agent import BaseDowAgent
from k9_dow.contracts.artifacts import DowAgentResult
from k9_dow.contracts.payloads import DowAgentPayload
from k9_dow.utils.markdown_utils import extract_first_json


class OperationalExtractorAgent(BaseDowAgent):
    layer = "DoW OperationalExtractor SBB"
    agent_name = "OperationalExtractorAgent"

    def run_agent(self, payload: DowAgentPayload) -> DowAgentResult:
        prompt = self.build_prompt(
            role="Operational Function and Process Analyst",
            task=(
                "Extract all operational functions, processes, and activities from the source.\n"
                "For each provide:\n"
                "- Function or process name\n"
                "- Description\n"
                "- Scope relation (which scope domain it belongs to)\n"
                "- Performers (who or what executes it, if stated)\n"
                "- Verbatim evidence from the source\n\n"
                "Map functions to OV-5 style activity decomposition where possible.\n\n"
                "If not found: NOT PROVIDED IN SOURCE\n\n"
                "Return Markdown report and JSON:\n"
                '{"operations": [{"name": "...", "description": "...", "scope_relation": "...", '
                '"performers": ["..."], "evidence": "..."}]}'
            ),
            source_text=payload.source_markdown,
            prior_outputs="\n".join(payload.prior_outputs.values()) if payload.prior_outputs else "",
        )

        raw = self.invoke_llm(prompt)
        json_str = extract_first_json(raw)
        json_data = json.loads(json_str) if json_str else {"operations": []}
        citations = [
            o.get("evidence", "")
            for o in json_data.get("operations", [])
            if o.get("evidence")
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
