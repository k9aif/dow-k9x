# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations
import json
from k9_dow.agents.src.base_dow_agent import BaseDowAgent
from k9_dow.contracts.artifacts import DowAgentResult
from k9_dow.contracts.payloads import DowAgentPayload
from k9_dow.utils.markdown_utils import extract_first_json


class ObjectiveExtractorAgent(BaseDowAgent):
    layer = "DoW ObjectiveExtractor SBB"
    agent_name = "ObjectiveExtractorAgent"

    def run_agent(self, payload: DowAgentPayload) -> DowAgentResult:
        prompt = self.build_prompt(
            role="Objectives Analyst",
            task=(
                "Extract all objectives, goals, and desired outcomes.\n"
                "For each provide:\n"
                "- Objective statement\n"
                "- Category (strategic/operational/technical)\n"
                "- Priority (if stated)\n"
                "- Verbatim evidence\n\n"
                "If none found, write: NOT PROVIDED IN SOURCE\n\n"
                "Return Markdown and JSON:\n"
                '{"objectives": [{"statement": "...", "category": "...", "priority": "...", "evidence": "..."}]}'
            ),
            source_text=payload.source_markdown,
            prior_outputs="\n".join(payload.prior_outputs.values()) if payload.prior_outputs else "",
        )

        raw = self.invoke_llm(prompt)
        json_str = extract_first_json(raw)
        json_data = json.loads(json_str) if json_str else {"objectives": []}
        citations = [o.get("evidence", "") for o in json_data.get("objectives", []) if o.get("evidence")]

        return DowAgentResult(
            job_id=payload.job_id,
            agent_name=self.agent_name,
            stage_id=payload.stage_id,
            status="completed",
            markdown=raw,
            json_data=json_data,
            citations=citations,
        )
