# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations
import json
from k9_dow.agents.src.base_dow_agent import BaseDowAgent
from k9_dow.contracts.artifacts import DowAgentResult
from k9_dow.contracts.payloads import DowAgentPayload
from k9_dow.utils.markdown_utils import extract_first_json


class SystemServiceExtractorAgent(BaseDowAgent):
    layer = "DoW SystemServiceExtractor SBB"
    agent_name = "SystemServiceExtractorAgent"

    def run_agent(self, payload: DowAgentPayload) -> DowAgentResult:
        prompt = self.build_prompt(
            role="Systems and Services Analyst",
            task=(
                "Extract all systems, services, and their interfaces from the source.\n"
                "For each system or service provide:\n"
                "- Name\n"
                "- Type (system/service/platform/application)\n"
                "- Description\n"
                "- Hosting system (if applicable)\n"
                "- Interfaces and dependencies\n"
                "- DoDAF mapping (SV-1 for systems, SvcV-1 for services)\n"
                "- Verbatim evidence from the source\n\n"
                "If not found: NOT PROVIDED IN SOURCE\n\n"
                "Return Markdown report and JSON:\n"
                '{"systems": [{"name": "...", "type": "...", "description": "...", '
                '"hosting": "...", "interfaces": ["..."], "dodaf_view": "...", "evidence": "..."}], '
                '"services": [{"name": "...", "type": "...", "description": "...", '
                '"provider": "...", "consumers": ["..."], "dodaf_view": "...", "evidence": "..."}]}'
            ),
            source_text=payload.source_markdown,
            prior_outputs="\n".join(payload.prior_outputs.values()) if payload.prior_outputs else "",
        )

        raw = self.invoke_llm(prompt)
        json_str = extract_first_json(raw)
        json_data = json.loads(json_str) if json_str else {"systems": [], "services": []}
        citations = []
        for item in json_data.get("systems", []) + json_data.get("services", []):
            if item.get("evidence"):
                citations.append(item["evidence"])

        return DowAgentResult(
            job_id=payload.job_id,
            agent_name=self.agent_name,
            stage_id=payload.stage_id,
            status="completed",
            markdown=raw,
            json_data=json_data,
            citations=citations,
        )
