# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations
import json
from k9_dow.agents.src.base_dow_agent import BaseDowAgent
from k9_dow.contracts.artifacts import DowAgentResult
from k9_dow.contracts.payloads import DowAgentPayload
from k9_dow.utils.markdown_utils import extract_first_json


class CapabilityExtractorAgent(BaseDowAgent):
    layer = "DoW CapabilityExtractor SBB"
    agent_name = "CapabilityExtractorAgent"

    def run_agent(self, payload: DowAgentPayload) -> DowAgentResult:
        prompt = self.build_prompt(
            role="Capability Analyst",
            task=(
                "Extract all capability references from the source document.\n"
                "For each capability provide:\n"
                "- Capability name\n"
                "- Description\n"
                "- Scope relation (which scope domain it maps to)\n"
                "- Associated operational activities (if stated)\n"
                "- Verbatim evidence from the source\n\n"
                "Align to CV-2 style capability taxonomy where possible.\n\n"
                "If not found: NOT PROVIDED IN SOURCE\n\n"
                "Return Markdown report and JSON:\n"
                '{"capabilities": [{"name": "...", "description": "...", '
                '"scope_relation": "...", "activities": ["..."], "evidence": "..."}]}'
            ),
            source_text=payload.source_markdown,
            prior_outputs="\n".join(payload.prior_outputs.values()) if payload.prior_outputs else "",
        )

        raw = self.invoke_llm(prompt)
        json_str = extract_first_json(raw)
        json_data = json.loads(json_str) if json_str else {"capabilities": []}
        citations = [
            c.get("evidence", "")
            for c in json_data.get("capabilities", [])
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
