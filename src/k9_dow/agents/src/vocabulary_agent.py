# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations
import json
from k9_dow.agents.src.base_dow_agent import BaseDowAgent
from k9_dow.contracts.artifacts import DowAgentResult
from k9_dow.contracts.payloads import DowAgentPayload
from k9_dow.utils.markdown_utils import extract_first_json


class VocabularyAgent(BaseDowAgent):
    layer = "DoW Vocabulary SBB"
    agent_name = "VocabularyAgent"

    def run_agent(self, payload: DowAgentPayload) -> DowAgentResult:
        prompt = self.build_prompt(
            role="Architecture Vocabulary and Terminology Analyst",
            task=(
                "Build an AV-2 Integrated Dictionary vocabulary seed from the source document.\n"
                "Extract all significant domain terms, acronyms, and definitions.\n"
                "For each entry provide:\n"
                "- Term\n"
                "- Definition (as stated in source, or inferred from context)\n"
                "- Category (acronym/concept/system/organization/standard/process)\n"
                "- Source reference (section or paragraph where term appears)\n\n"
                "Group terms alphabetically.\n\n"
                "If no significant terminology found, write: NOT PROVIDED IN SOURCE\n\n"
                "Return Markdown report and JSON:\n"
                '{"vocabulary": [{"term": "...", "definition": "...", "category": "...", '
                '"source_reference": "..."}]}'
            ),
            source_text=payload.source_markdown,
            prior_outputs="\n".join(payload.prior_outputs.values()) if payload.prior_outputs else "",
        )

        raw = self.invoke_llm(prompt)
        json_str = extract_first_json(raw)
        json_data = json.loads(json_str) if json_str else {"vocabulary": []}

        return DowAgentResult(
            job_id=payload.job_id,
            agent_name=self.agent_name,
            stage_id=payload.stage_id,
            status="completed",
            markdown=raw,
            json_data=json_data,
        )
