# SPDX-License-Identifier: Apache-2.0
"""A reviewer-facing summary of a gate's readiness assessment, as name-value pairs for the K9X HIL task.

The readiness scorer writes Markdown (tables, bold, headings). HIL shows payload values as plain text, so
the raw Markdown is unreadable there. This pulls out what a decision authority needs at a glance: the
score, the status, each entry criterion (met / not met), the blockers and the recommendation. The full
assessment stays in the review package, linked from the task. Anything that cannot be read reliably is
left out rather than guessed; if nothing can be read, the summary points to the package instead.
"""

from __future__ import annotations

import re
from typing import Dict, List, Optional

_SCORE = re.compile(r"(?:Overall\s+Readiness\s+Score|Total)\**\s*:?\**\s*\**\s*(\d{1,3}(?:\.\d+)?)\s*/\s*100", re.I)
_STATUS = re.compile(r"\*\*(?:Status|Gate\s+Disposition)\s*:\*\*\s*([A-Z][A-Z /_-]*[A-Z])", re.I)
_RECOMMENDATION = re.compile(r"\*\*Recommendation(?:\s+for\s+Decision\s+Authority)?\s*:\*\*\s*(.+)", re.I)
_RECOMMENDATION_HEADING = re.compile(r"^#+\s*(?:\d+\.\s*)?Recommendation\b.*$", re.I | re.M)
_LABEL = re.compile(r"^(?:Recommendation|Status|Blocker|Critical|Issue)\s*:\s*", re.I)
_BLOCKER = re.compile(r"\*\*(?:BLOCKER|CRITICAL)\s*:?\s*\**\s*:?\s*(.+?)\*\*", re.I)


def _clean(text: str, limit: int = 160) -> str:
    text = re.sub(r"<br\s*/?>.*$", "", text, flags=re.I)        # table cells continue after <br>
    text = re.sub(r"[*`_#|$]+", "", text).strip(" .:-")
    text = _LABEL.sub("", re.sub(r"\s+", " ", text)).strip(" .:-")
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def _first_sentence(text: str) -> str:
    return re.split(r"(?<=[.!?])\s", text.strip(), maxsplit=1)[0]


def _criterion_status(assessment: str, criterion: str) -> str:
    """Met / Not met / Partially met for one entry criterion, from the line that names it."""
    for line in assessment.splitlines():
        if criterion.lower() in line.lower():
            row = line.upper()
            if re.search(r"NOT[\s_-]*MET", row):
                return "✗ Not met"
            if "PARTIAL" in row:
                return "◐ Partially met"
            if re.search(r"\bMET\b", row):
                return "✓ Met"
    return ""


def _key(text: str) -> str:
    """For de-duplication: lower case, no parenthetical notes."""
    return re.sub(r"\s*\(.*?\)", "", text).lower().strip()


def _blockers(text: str) -> List[str]:
    """Bullet items under a 'Blockers' heading; else bold BLOCKER/CRITICAL labels anywhere."""
    found: List[str] = []
    section = re.search(r"^#+\s*(?:\d+\.\s*)?Blockers?\b.*?$(.*?)(?=^#+\s|\Z)", text, re.I | re.M | re.S)
    if section:
        for line in section.group(1).splitlines():
            m = re.match(r"\s*(?:[-*]|\d+\.)\s+(.*)", line)
            if m:
                item = _clean(m.group(1), 120)
                if item and not re.match(r"(?:Impact|Action Required|Evidence|Rationale|Reason)\b", item, re.I):
                    found.append(item)
    if not found:
        found = [_clean(m.group(1), 120) for m in _BLOCKER.finditer(text)]
    unique: List[str] = []
    for b in found:
        if b and len(b) > 3 and not any(_key(b) == _key(u) or _key(b) in _key(u) for u in unique):
            unique = [u for u in unique if _key(u) not in _key(b)] + [b]
    return unique


def _recommendation(text: str) -> str:
    m = _RECOMMENDATION.search(text)
    if m and _clean(m.group(1)):
        return _clean(_first_sentence(m.group(1)))
    h = _RECOMMENDATION_HEADING.search(text)
    if h:
        for line in text[h.end():].splitlines():
            if line.strip():
                return _clean(_first_sentence(line))
    return ""


def summarize_readiness(assessment: str, criteria: List[str], score: Optional[int] = None) -> Dict[str, str]:
    """Ordered name-value pairs for the HIL task payload. ``score`` is the computed readiness score
    (gates/readiness.py); when given it is the one shown."""
    text = assessment or ""
    summary: Dict[str, str] = {}

    stated = _SCORE.search(text)
    value = str(score) if score is not None else (stated.group(1) if stated else "")
    status = _STATUS.search(text)
    if value or status:
        parts = [f"{value} / 100" if value else "", _clean(status.group(1)).upper() if status else ""]
        summary["Readiness"] = " — ".join(p for p in parts if p)

    for i, criterion in enumerate(criteria, 1):
        verdict = _criterion_status(text, criterion)
        if verdict:
            summary[f"{i}. {criterion}"] = verdict

    blockers = _blockers(text)
    if blockers:
        summary["Blockers"] = "; ".join(blockers[:3])

    rec = _recommendation(text)
    if rec:
        summary["Recommendation"] = rec

    if not summary:
        summary["Readiness assessment"] = "See the review package (View link under Artifacts)"
    return summary
