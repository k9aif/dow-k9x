# SPDX-License-Identifier: Apache-2.0
# K9-AIF Framework — DAS real governance backend

"""
GuardianGovernance — real governance for DAS, backed by the
granite4.1-guardian model already running on the same Ollama instance
DAS's other agents use.

Scoped at the orchestrator level (constructed once by JcidsOrchestrator,
called around execute_flow()), not per-agent and not via the shared
BaseSquad framework class -- touching all 17 agents individually, or
BaseSquad.execute() (which every squad-based app, including k9chat,
shares) was rejected as too broad a change this close to the IEEE
Access submission. See project_k9aif_architecture_facts memory,
2026-09-03 decision.

Matches k9chat's own GuardAgent pattern exactly (same InferenceRequest/
task_type="guardrails"/llm_invoke() call) -- purpose-built guardian
models are tuned via their own Ollama Modelfile to answer a content-risk
question directly from the raw input, no wrapper prompt needed.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from k9_aif_abb.k9_inference.models.inference_request import InferenceRequest
from k9_aif_abb.k9_utils.llm_invoke import llm_invoke

log = logging.getLogger(__name__)


class GuardianGovernance:
    """Implements the same pre_process/post_process contract as
    NoopGovernance (k9_core/governance/pipeline.py), so it's a drop-in
    replacement wherever governance is currently NoopGovernance.

    pre_process is a passthrough -- input screening isn't this
    governance's job for a review-generation tool. ModelExtractorAgent
    already treats the uploaded source document as trusted material per
    DoDAF Agent Rule #1 ("use only information present in source"); the
    meaningful check is on what DAS is about to hand to a human
    reviewer, not the raw input.

    post_process reviews the assembled JCIDS package content and
    ATTACHES its verdict to the payload rather than raising/blocking --
    consistent with DAS's "AI recommends, human decides" pattern used
    everywhere else (readiness scores, gap reports are all advisory to
    the human decision authority, never auto-enforced). A Guardian flag
    becomes something the JROC reviewer sees and weighs, not a silent
    auto-reject that could misfire on legitimate defense-acquisition
    terminology (weapons, interceptors, threat descriptions) a
    general-purpose safety classifier was never tuned to distinguish
    from real harm -- a real risk given DAS's actual subject matter.
    """

    def __init__(self, config: Dict[str, Any]):
        self._config = config

    def pre_process(self, payload: dict, ctx: Optional[dict] = None) -> dict:
        return payload

    def post_process(self, payload: dict, ctx: Optional[dict] = None) -> dict:
        text = self._extract_reviewable_text(payload)
        if not text:
            payload["governance"] = {"checked": False, "flagged": False, "reason": "no reviewable content"}
            return payload

        try:
            req = InferenceRequest(
                prompt=text[:4000],
                task_type="guardrails",
                metadata={"agent": "GuardianGovernance"},
            )
            resp = llm_invoke(self._config, req)
            verdict = (resp.output or "").strip().lower()
            # granite4.1-guardian:8b wraps its verdict as "<score> yes
            # </score>" / "<score> no </score>", not a bare yes/no --
            # verified 2026-09-03 against real benign and clearly-harmful
            # test content. .startswith("yes") (the naive check, matching
            # k9chat's own GuardAgent) silently never matches "<score>
            # yes </score>" -- caught only by testing an actual harmful
            # case, not just a benign one; a startswith-only check would
            # have made this governance check permanently a no-op while
            # still reporting "checked": True.
            flagged = "yes" in verdict
            payload["governance"] = {
                "checked": True,
                "flagged": flagged,
                "guardian_output": resp.output,
                "model": resp.model_alias,
            }
            if flagged:
                log.warning(
                    "[GuardianGovernance] Content flagged for job=%s: %s",
                    payload.get("job_id"), resp.output,
                )
            else:
                log.info("[GuardianGovernance] Passed for job=%s", payload.get("job_id"))
        except Exception as exc:
            log.warning("[GuardianGovernance] Guardian check failed, proceeding unchecked: %s", exc)
            payload["governance"] = {"checked": False, "flagged": False, "error": str(exc)}

        return payload

    @staticmethod
    def _extract_reviewable_text(payload: dict) -> str:
        """Pull the OV-1 view's actual generated prose -- the human-
        readable output a JROC reviewer would see -- not the raw JSON
        structure around it. ViewGeneratorAgent's result is double-
        wrapped (BaseValidationLoopAgent._to_dict()'s own "output" key,
        containing ValidationLoopResult.output's "output" key with the
        real text) -- handled defensively since that nesting is easy to
        get wrong and there's no schema enforcing it.
        """
        view_gen = payload.get("view_generation", {})
        generated = view_gen.get("generated_views", {}) if isinstance(view_gen, dict) else {}
        if not isinstance(generated, dict):
            return ""

        outer = generated.get("output", "")
        if isinstance(outer, str):
            return outer
        if isinstance(outer, dict):
            inner = outer.get("output", "")
            if isinstance(inner, str):
                return inner
        return ""
