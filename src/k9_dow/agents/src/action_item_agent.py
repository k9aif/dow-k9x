# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations
import json
from k9_dow.agents.src.base_dow_agent import BaseDowAgent
from k9_dow.contracts.artifacts import DowAgentResult
from k9_dow.contracts.payloads import DowAgentPayload
from k9_dow.utils.markdown_utils import extract_first_json


class ActionItemAgent(BaseDowAgent):
    layer = "DoW ActionItem SBB"
    agent_name = "ActionItemAgent"

    def run_agent(self, payload: DowAgentPayload) -> DowAgentResult:
        prompt = self.build_prompt(
            role="Architecture Action Planning Specialist",
            task=(
                "Generate prioritized action items from all analysis findings.\n\n"
                "Review all prior outputs for:\n"
                "- Capability gaps\n"
                "- Operational weaknesses\n"
                "- Architecture alignment issues\n"
                "- Risk findings\n"
                "- Cross-view consistency issues\n"
                "- Missing evidence or data gaps\n\n"
                "For each action item provide:\n"
                "- Action ID (ACT-NNN)\n"
                "- Title\n"
                "- Description\n"
                "- Priority (critical/high/medium/low)\n"
                "- Category (architecture/operational/system/governance)\n"
                "- Responsible viewpoint owner\n"
                "- Originating finding\n\n"
                "Order by priority (critical first), then by category.\n\n"
                "If no findings to act on: NOT PROVIDED IN SOURCE\n\n"
                "Return Markdown report and JSON:\n"
                '{"action_items": [{"id": "ACT-001", "title": "...", '
                '"description": "...", "priority": "...", "category": "...", '
                '"owner": "...", "finding": "..."}]}'
            ),
            source_text=payload.source_markdown,
            prior_outputs="\n".join(payload.prior_outputs.values()) if payload.prior_outputs else "",
        )

        raw = self.invoke_llm(prompt)
        json_str = extract_first_json(raw)
        json_data = json.loads(json_str) if json_str else {"action_items": []}

        return DowAgentResult(
            job_id=payload.job_id,
            agent_name=self.agent_name,
            stage_id=payload.stage_id,
            status="completed",
            markdown=raw,
            json_data=json_data,
        )
