# SPDX-License-Identifier: Apache-2.0
"""The gate readiness score, computed in code.

The readiness scorer (a language model) judges each entry criterion: MET, PARTIALLY_MET or NOT_MET,
with rationale. The overall score is arithmetic over those verdicts and the gate's criterion weights
(gate_registry), so it is computed here, not by the model: one score, the same in the HIL task, the
ICD and the Milestone package. (JOB-20261008-DFA941: the model wrote 40/100, then "corrected" it to
70/100; its own weights gave 60.)
"""

from __future__ import annotations

import re
from datetime import date
from typing import Dict, List, Optional, Sequence

MET, PARTIALLY_MET, NOT_MET = "MET", "PARTIALLY_MET", "NOT_MET"
CREDIT = {MET: 1.0, PARTIALLY_MET: 0.5, NOT_MET: 0.0}
LABEL = {MET: "Met", PARTIALLY_MET: "Partially met", NOT_MET: "Not met"}

_VERDICT = re.compile(r"\b(NOT[\s_-]*MET|PARTIAL(?:LY)?[\s_-]*MET|MET)\b", re.I)
_DATE_PLACEHOLDER = re.compile(r"\[(?:Current\s+Date|Date|Insert\s+Date|Today'?s?\s+Date)\]", re.I)
_MODEL_SCORE_LINE = re.compile(
    r"^.*(?:Overall\s+(?:Readiness\s+)?Score|Total\s+Score|Weighted\s+(?:Overall\s+)?Score).*\d+(?:\.\d+)?\s*/\s*100.*$\n?"
    r"|^\s*\**\s*\*?Correction\b.*$\n?"
    r"|^.*Assessment\s+Date\s*:.*$\n?", re.I | re.M)
_SCORE_SECTION = re.compile(r"^(#+)\s*[^\n]*Score\s+Calculation[^\n]*\n.*?(?=^#{1,6}\s|\Z)", re.I | re.M | re.S)


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[*`_|#]+", " ", text)).strip().lower()


def _verdict(text: str) -> Optional[str]:
    m = _VERDICT.search(text.upper())
    if not m:
        return None
    token = m.group(1).upper()
    if token.startswith("NOT"):
        return NOT_MET
    if token.startswith("PARTIAL"):
        return PARTIALLY_MET
    return MET


def criterion_verdicts(assessment: str, criteria: Sequence[str]) -> List[Optional[str]]:
    """The verdict for each criterion, in order (None where it can't be read).

    A criterion is found by its text, or by its number ('Criterion 3', '| 3 |', '3.'); the verdict is
    on that line or, for list-style assessments ('Criterion 4: …' then '• Score: MET'), within the next
    few lines before another criterion starts."""
    lines = (assessment or "").splitlines()
    normed = [_norm(line) for line in lines]
    names = [_norm(c) for c in criteria]

    def starts(i: int, idx: int) -> bool:
        line = normed[idx]
        return names[i] in line or bool(
            re.match(rf"^(?:criterion\s*)?{i + 1}\s*[.:)]?\s", line) and len(line) > 3
            and any(w in line for w in names[i].split()[:2]))

    verdicts: List[Optional[str]] = []
    for i in range(len(criteria)):
        found = None
        for idx in range(len(lines)):
            if not starts(i, idx):
                continue
            for k in range(idx, min(idx + 5, len(lines))):
                if k > idx and any(starts(j, k) for j in range(len(criteria)) if j != i):
                    break
                found = _verdict(lines[k].replace(criteria[i], "").replace(criteria[i].upper(), ""))
                if found:
                    break
            if found:
                break
        verdicts.append(found)
    return verdicts


def weights_for(gate_id: str, n: int) -> List[int]:
    from k9_dow.gates.gate_registry import DAS_GATES
    gate = DAS_GATES.get(gate_id)
    weights = list(gate.criterion_weights) if gate else []
    return weights if len(weights) == n else [1] * n


def readiness_score(verdicts: Sequence[Optional[str]], weights: Sequence[int]) -> Optional[int]:
    """Weighted score 0–100; None if any verdict is missing (never guessed)."""
    if not verdicts or any(v is None for v in verdicts):
        return None
    total = sum(weights)
    return round(100 * sum(w * CREDIT[v] for v, w in zip(verdicts, weights)) / total) if total else None


def fill_date(text: str, when: Optional[str] = None) -> str:
    """Replace '[Current Date]'-style placeholders the model leaves in its text."""
    return _DATE_PLACEHOLDER.sub(when or date.today().isoformat(), text or "")


def score_block(criteria: Sequence[str], verdicts: Sequence[Optional[str]], weights: Sequence[int],
                score: Optional[int], when: str) -> str:
    total = sum(weights) or 1
    rows = []
    for i, (c, v, w) in enumerate(zip(criteria, verdicts, weights), 1):
        points = "–" if v is None else f"{round(100 * w * CREDIT[v] / total, 1):g}"
        rows.append(f"| {i} | {c} | {LABEL.get(v, 'Not stated')} | {round(100 * w / total, 1):g}% | {points} |")
    rows = "\n".join(rows)
    if score is None:
        headline = ("**Overall Readiness Score:** not computed: the assessment does not state a verdict "
                    "for every criterion (see the table)")
    else:
        headline = f"**Overall Readiness Score:** {score}/100"
    return (f"**Assessment Date:** {when}\n\n{headline}\n\n"
            "The score is computed from the per-criterion verdicts and the gate's criterion weights "
            "(Met: full weight, Partially met: half, Not met: none).\n\n"
            "| # | Criterion | Verdict | Weight | Points |\n| --- | --- | --- | --- | --- |\n"
            f"{rows}\n")


def apply_computed_score(assessment: str, gate_id: str, criteria: Sequence[str],
                         when: Optional[str] = None) -> Dict[str, object]:
    """The scorer's assessment with any model-written score removed and the computed score block put
    after the title; returns the text, score and verdicts."""
    when = when or date.today().isoformat()
    text = fill_date(assessment or "", when)
    verdicts = criterion_verdicts(text, criteria)
    weights = weights_for(gate_id, len(criteria))
    score = readiness_score(verdicts, weights)
    text = _SCORE_SECTION.sub("", text)
    text = _MODEL_SCORE_LINE.sub("", text)
    block = score_block(criteria, verdicts, weights, score, when)
    title = re.match(r"\s*#\s[^\n]*\n", text)
    text = (text[: title.end()] + "\n" + block + "\n" + text[title.end():].lstrip("\n")) if title \
        else block + "\n" + text.lstrip("\n")
    return {"output": text, "score": score,
            "verdicts": {c: v for c, v in zip(criteria, verdicts)}}


_STATED_SCORE = re.compile(
    r"(?im)^(.*?(?:Readiness\s+Score|Overall\s+Score|Total\s+Score)\**\s*:?\s*\**\s*)(?=[^\n]*\d+(?:\.\d+)?\s*/\s*100)[^\n]*$")


def computed_score(context: Dict[str, object]) -> Optional[int]:
    """The computed score carried by the readiness step (in a squad's context or a stage's prior outputs)."""
    step = context.get("readiness_score") if isinstance(context, dict) else None
    return step.get("score") if isinstance(step, dict) else None


def align_score(text: str, score: Optional[int], when: Optional[str] = None) -> str:
    """Downstream text (gap report, review package) states the computed score, never a model's own:
    any score it restates is set to the computed one, recalculations and 'Correction' notes are
    dropped, date placeholders are filled."""
    text = fill_date(text, when)
    if score is None:
        return text
    text = _SCORE_SECTION.sub("", text)
    text = re.sub(r"(?im)^\s*\**\s*\*?Correction\b.*$\n?", "", text)
    return _STATED_SCORE.sub(lambda m: f"{m.group(1)}{score}/100", text)
