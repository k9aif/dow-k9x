# SPDX-License-Identifier: Apache-2.0
# K9-AIF Framework
"""Context enrichment inside a squad.

BaseSquad keeps each step's result under its ``result_key`` in the shared
context, so a later agent reads what earlier agents produced in *this* squad
(``payload["evidence"]``, ``payload["readiness_score"]``, ...).
``prior_outputs`` is different: the previous *stage's* results, passed in by
the orchestrator.
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List


def step_output(payload: Dict[str, Any], result_key: str) -> str:
    """Text output of an earlier step in this squad ('' if it hasn't run)."""
    value = payload.get(result_key)
    if isinstance(value, dict):
        return str(value.get("output") or "")
    return str(value or "")


def gate_criteria(payload: Dict[str, Any]) -> List[str]:
    """Entry criteria for this gate: as loaded by CriteriaLoaderAgent
    (``criteria`` step), else as passed in by the orchestrator."""
    loaded = payload.get("criteria")
    if isinstance(loaded, dict) and loaded.get("criteria"):
        return list(loaded["criteria"])
    return list(payload.get("gate_criteria") or [])


def prior_text(prior: Any) -> str:
    """The previous stage's results as text for a prompt: each result's ``output``, not the whole record.
    A validation-loop result also carries every iteration and its evidence (about 99,000 characters for one
    generated view); rendering ``prior_outputs`` whole sent all of that to the model (v1.3.7 and earlier)."""
    if not prior:
        return "(none)"
    if isinstance(prior, str):
        return prior
    parts = []
    for key, value in prior.items():
        if key in ("status", "squad_id"):
            continue
        if isinstance(value, dict) and "output" in value:
            value = value["output"]
        elif not isinstance(value, str):
            value = json.dumps(value, default=str, indent=1)
        parts.append(f"### {key}\n{value}")
    return "\n\n".join(parts)


# Conservative: these documents measure about 4 characters per qwen3.8 token; 3 errs toward refusing.
CHARS_PER_TOKEN = 3.0
OUTPUT_RESERVE = 2048


def assert_fits_window(prompt: str, agent: str = "") -> None:
    """Refuse a prompt that would exceed the model's context window. Ollama drops the oldest part of a
    prompt longer than num_ctx without an error, so the model would read part of its input and the run
    would look normal. The failure goes up to the stage, which records it (Retry)."""
    window = int(os.environ.get("OLLAMA_NUM_CTX") or 32768)
    estimate = int(len(prompt) / CHARS_PER_TOKEN)
    if estimate + OUTPUT_RESERVE > window:
        raise RuntimeError(f"{agent or 'agent'}: prompt of about {estimate} tokens does not fit the "
                           f"{window}-token context window (it would be truncated without an error)")
