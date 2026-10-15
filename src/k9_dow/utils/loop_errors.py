# SPDX-License-Identifier: Apache-2.0
# K9-AIF Framework
"""Loop agents pass a failed step up to the squad instead of returning it as output.

K9ValidationLoopAgent catches an exception from run_validation() (a model call that
failed after llm_invoke's retries) and returns a FAIL result whose output is
{"reason": "validation_failed"}. The squad would carry that on as the agent's
output and the package would be written around it. In DAS a failed step fails
the stage instead, so the orchestrator records it and offers a retry.
"""

from __future__ import annotations


def raise_if_step_failed(layer: str, loop_ctx) -> None:
    """Raise the failed step's error, if the loop ended because a step raised."""
    last = loop_ctx.steps[-1] if loop_ctx.steps else None
    error = (last.observation or {}).get("error") if last and last.tool_result is None else None
    if error:
        raise RuntimeError(f"{layer}: step {last.iteration} failed: {error}")
