# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import json
import logging
from typing import Any, Dict

from k9_dow.agents.src.base_dow_agent import BaseDowAgent
from k9_dow.contracts.artifacts import DowAgentResult, GovernanceFinding
from k9_dow.contracts.payloads import DowAgentPayload
from k9_dow.utils.markdown_utils import extract_first_json

log = logging.getLogger(__name__)


class GovernanceAgent(BaseDowAgent):
    """
    Reviews stage outputs against governance rules.

    Checks for invented content, missing citations, and compliance
    with DoD evidence-grounding requirements.
    """

    layer = "DoW Governance SBB"
    agent_name = "GovernanceAgent"

    def run_agent(self, payload: DowAgentPayload) -> DowAgentResult:
        prior_text = (
            "\n\n".join(payload.prior_outputs.values())
            if payload.prior_outputs
            else ""
        )

        if not prior_text.strip():
            return DowAgentResult(
                job_id=payload.job_id,
                agent_name=self.agent_name,
                stage_id=payload.stage_id,
                status="completed",
                markdown="## Governance Review\n\nNo prior outputs to review.\n\n**Status:** pass",
                json_data={
                    "status": "pass",
                    "findings": [],
                    "summary": "No content to review",
                },
            )

        prompt = self.build_prompt(
            role="DoD Architecture Governance Reviewer",
            task=(
                "Review the following stage outputs against these governance rules:\n\n"
                f"{self._governance_rules}\n\n"
                "Return JSON:\n"
                '{"status": "pass|warn|block", "findings": [{"severity": "info|warning|error|blocker", '
                '"rule_id": "G1-G10", "message": "...", "evidence": "..."}], "summary": "..."}'
            ),
            source_text=prior_text[:6000],
        )

        try:
            raw = self.invoke_llm(prompt, task_type="reasoning")
            json_str = extract_first_json(raw)
            if json_str:
                data = json.loads(json_str)
            else:
                data = {
                    "status": "pass",
                    "findings": [],
                    "summary": "Governance review completed (no JSON returned)",
                }
        except Exception as exc:
            log.warning("[GovernanceAgent] LLM review failed: %s", exc)
            data = {
                "status": "warn",
                "findings": [],
                "summary": f"Governance review failed: {exc}",
            }

        status = data.get("status", "pass")
        md = f"## Governance Review\n\n**Status:** {status}\n\n{data.get('summary', '')}\n"
        if data.get("findings"):
            md += "\n### Findings\n"
            for f in data["findings"]:
                md += f"- **[{f.get('severity', 'info')}] {f.get('rule_id', '')}:** {f.get('message', '')}\n"

        return DowAgentResult(
            job_id=payload.job_id,
            agent_name=self.agent_name,
            stage_id=payload.stage_id,
            status="completed",
            markdown=md,
            json_data=data,
        )
