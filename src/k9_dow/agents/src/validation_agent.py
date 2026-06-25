# SPDX-License-Identifier: Apache-2.0
# DoW Architecture Workbench — ValidationAgent (SBB)
#
# Validates document readability, minimum content length, and basic
# structural requirements before pipeline execution.
# Pure extraction — no LLM.

import re
from typing import Any, Dict, Optional

from k9_aif_abb.k9_core.agent.base_agent import BaseAgent

MIN_CHARS = 500


class ValidationAgent(BaseAgent):

    layer = "DoW Validation SBB"

    def __init__(self, config: Optional[Dict[str, Any]] = None, monitor=None, **kwargs):
        super().__init__(config or {}, monitor=monitor, **kwargs)

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        text = payload.get("source_markdown") or payload.get("normalized_markdown") or ""
        warnings = []

        char_count = len(text)
        line_count = text.count("\n") + 1
        has_headings = bool(re.search(r"^#{1,6}\s", text, re.MULTILINE))
        has_paragraphs = line_count > 5
        is_valid = char_count >= MIN_CHARS

        if char_count < MIN_CHARS:
            warnings.append(f"Document too short ({char_count} chars, minimum {MIN_CHARS})")
        if not has_headings:
            warnings.append("No Markdown headings detected")

        self.publish_event({
            "type": "ValidationCompleted",
            "agent": "ValidationAgent",
            "valid": is_valid,
            "char_count": char_count,
        })

        return {
            "agent": "ValidationAgent",
            "valid": is_valid,
            "char_count": char_count,
            "line_count": line_count,
            "has_structure": has_headings or has_paragraphs,
            "warnings": warnings,
            "output": (
                f"## Document Validation\n\n"
                f"- **Valid:** {'Yes' if is_valid else 'No'}\n"
                f"- **Character count:** {char_count}\n"
                f"- **Line count:** {line_count}\n"
                f"- **Has headings:** {'Yes' if has_headings else 'No'}\n"
            ),
        }
