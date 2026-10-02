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
