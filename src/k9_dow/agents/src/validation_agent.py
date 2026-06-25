# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import re
from typing import Any, Dict

from k9_dow.agents.src.base_dow_agent import BaseDowAgent
from k9_dow.contracts.artifacts import DowAgentResult
from k9_dow.contracts.payloads import DowAgentPayload

MIN_CHARS = 500


class ValidationAgent(BaseDowAgent):
    """
    Validates document readability, minimum content length, and basic
    structural requirements before pipeline execution.

    Pure extraction agent — no LLM invocation.
    """

    layer = "DoW Validation SBB"
    agent_name = "ValidationAgent"

    def run_agent(self, payload: DowAgentPayload) -> DowAgentResult:
        text = payload.source_markdown or ""
        warnings: list[str] = []
        missing: list[str] = []

        char_count = len(text)
        line_count = text.count("\n") + 1
        has_headings = bool(re.search(r"^#{1,6}\s", text, re.MULTILINE))
        has_paragraphs = line_count > 5

        if char_count < MIN_CHARS:
            missing.append(f"Document too short ({char_count} chars, minimum {MIN_CHARS})")

        if not has_headings:
            warnings.append("No Markdown headings detected")

        if not has_paragraphs:
            warnings.append("Very few lines — may lack sufficient structure")

        is_valid = char_count >= MIN_CHARS

        return DowAgentResult(
            job_id=payload.job_id,
            agent_name=self.agent_name,
            stage_id=payload.stage_id,
            status="completed",
            markdown=(
                f"## Document Validation\n\n"
                f"- **Valid:** {'Yes' if is_valid else 'No'}\n"
                f"- **Character count:** {char_count}\n"
                f"- **Line count:** {line_count}\n"
                f"- **Has headings:** {'Yes' if has_headings else 'No'}\n"
                f"- **Has paragraphs:** {'Yes' if has_paragraphs else 'No'}\n"
            ),
            json_data={
                "valid": is_valid,
                "char_count": char_count,
                "line_count": line_count,
                "has_structure": has_headings or has_paragraphs,
                "missing_elements": missing,
            },
            warnings=warnings,
        )
