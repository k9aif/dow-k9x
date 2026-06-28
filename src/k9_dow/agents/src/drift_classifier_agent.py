from __future__ import annotations

from k9_aif_abb.k9_agents.validation import (
    K9ValidationLoopAgent,
    ValidationDisposition,
    ValidationLoopContext,
    ValidationLoopResult,
)
from k9_aif_abb.k9_inference.models.inference_request import InferenceRequest
from k9_aif_abb.k9_utils.llm_invoke import llm_invoke


class DriftClassifierAgent(K9ValidationLoopAgent):
    """Classifies detected drifts by severity. Iterates to verify
    severity calibration is accurate before reporting.

    4Ds: Augmentation — classifies severity, human reviews critical drifts.
    Uses stronger reasoning model for classification accuracy."""

    layer = "DAS DriftClassifier"

    def __init__(self, config=None, monitor=None, **kwargs):
        super().__init__(config or {}, monitor=monitor, **kwargs)

    def generate_hypothesis(self, loop_ctx: ValidationLoopContext):
        prior = loop_ctx.payload.get("prior_outputs", {})
        return {
            "drifts": prior,
            "iteration": loop_ctx.iteration,
        }

    def run_validation(self, hypothesis, loop_ctx: ValidationLoopContext):
        prev_classification = ""
        if loop_ctx.steps:
            prev_classification = (
                f"\nPrevious classification (verify and refine):\n"
                f"{loop_ctx.steps[-1].observation.get('classification', '')[:2000]}"
            )

        req = InferenceRequest(
            prompt=(
                f"Role: {self.config.get('role', 'Cross-Process Drift Classifier')}\n"
                f"Goal: {self.config.get('goal', 'Classify drift severity accurately')}\n\n"
                f"Detected drifts:\n{hypothesis['drifts']}\n"
                f"{prev_classification}\n\n"
                "For each drift classify:\n"
                "- Severity: INFO / WARNING / CRITICAL\n"
                "- Process: JCIDS / SE / PPBE / cross-process\n"
                "- Action: update baseline / re-fund / escalate / accept risk\n"
                "- Gate impact: does this block a pending gate?\n"
                "- Confidence in severity assessment (0.0-1.0)\n\n"
                "Output as structured drift alert report."
            ),
            metadata={"agent": self.layer},
            task_type=self.config.get("model", "reasoning"),
        )
        resp = llm_invoke(self.config, req)
        return {"output": resp.output}

    def evaluate_observation(self, tool_result, loop_ctx: ValidationLoopContext):
        output = tool_result.get("output", "")
        has_severity = any(s in output.upper() for s in ["INFO", "WARNING", "CRITICAL"])
        has_action = any(a in output.lower() for a in ["update baseline", "escalate", "accept risk"])
        confidence = min(0.95, 0.5 + (0.25 if has_severity else 0) + (0.2 if has_action else 0))
        return {"classification": output, "confidence": confidence}

    def should_continue(self, observation, loop_ctx: ValidationLoopContext):
        threshold = self.config.get("confidence_threshold", 0.8)
        if observation["confidence"] >= threshold:
            return ValidationDisposition.FINALIZE
        if loop_ctx.iteration >= self.config.get("max_iterations", 3):
            return ValidationDisposition.FINALIZE
        return ValidationDisposition.CONTINUE

    def finalize(self, loop_ctx: ValidationLoopContext) -> ValidationLoopResult:
        last = loop_ctx.steps[-1] if loop_ctx.steps else None
        output = last.observation.get("classification", "") if last else ""
        confidence = last.confidence if last else 0.0

        self.publish_event({"type": "AgentCompleted", "agent": self.layer})
        return ValidationLoopResult(
            disposition=ValidationDisposition.FINALIZE,
            output={"agent": self.layer, "output": output},
            steps=loop_ctx.steps,
            iterations=loop_ctx.iteration,
            final_confidence=confidence,
            evidence=[str(s.observation) for s in loop_ctx.steps],
        )
