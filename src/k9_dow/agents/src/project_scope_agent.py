# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations
import json
from k9_dow.agents.src.base_dow_agent import BaseDowAgent
from k9_dow.contracts.artifacts import DowAgentResult
from k9_dow.contracts.payloads import DowAgentPayload
from k9_dow.utils.markdown_utils import extract_first_json


class ProjectScopeAgent(BaseDowAgent):
    layer = "DoW ProjectScope SBB"
    agent_name = "ProjectScopeAgent"

    def run_agent(self, payload: DowAgentPayload) -> DowAgentResult:
        prompt = self.build_prompt(
            role="Architecture Scope Analyst",
            task=(
                "Extract the architecture project scope from the source document.\n"
                "Identify and structure:\n"
                "- Problem statement\n"
                "- Scope domains (operational, systems, services, technical standards)\n"
                "- Scope boundaries (what is in-scope and out-of-scope)\n"
                "- Level-of-detail required\n"
                "- Time horizon\n\n"
                "For each element provide verbatim evidence from the source.\n\n"
                "If not found: NOT PROVIDED IN SOURCE\n\n"
                "Return Markdown report and JSON:\n"
                '{"problem_statement": "...", '
                '"scope_domains": [{"domain": "...", "description": "...", "evidence": "..."}], '
                '"boundaries": {"in_scope": ["..."], "out_of_scope": ["..."]}, '
                '"level_of_detail": "...", '
                '"time_horizon": "..."}'
            ),
            source_text=payload.source_markdown,
            prior_outputs="\n".join(payload.prior_outputs.values()) if payload.prior_outputs else "",
        )

        raw = self.invoke_llm(prompt)
        json_str = extract_first_json(raw)
        json_data = json.loads(json_str) if json_str else {"scope_domains": []}
        citations = [
            d.get("evidence", "")
            for d in json_data.get("scope_domains", [])
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
