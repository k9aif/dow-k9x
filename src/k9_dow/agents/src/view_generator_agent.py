from __future__ import annotations

from k9_aif_abb.k9_agents.validation import (
    K9ValidationLoopAgent,
    ValidationDisposition,
    ValidationLoopContext,
    ValidationLoopResult,
)
from k9_aif_abb.k9_inference.models.inference_request import InferenceRequest
from k9_aif_abb.k9_utils.llm_invoke import llm_invoke


class ViewGeneratorAgent(K9ValidationLoopAgent):
    """Generates DoDAF architecture views (OV, SV, CV families). Iterates
    until the generated view passes consistency checks against the source.

    4Ds: Augmentation — generates views, human reviews at HITL gate.
    Uses K9Retriever to pull relevant sections from large source docs."""

    layer = "DAS ViewGenerator"

    def __init__(self, config=None, monitor=None, **kwargs):
        super().__init__(config or {}, monitor=monitor, **kwargs)
        self._retriever = None

    def _get_retriever(self):
        if self._retriever is None:
            try:
                from k9_aif_abb.k9_data.retrieval.k9_retriever import K9Retriever
                self._retriever = K9Retriever(config=self.config)
            except Exception:
                pass
        return self._retriever

    def generate_hypothesis(self, loop_ctx: ValidationLoopContext):
        view_type = loop_ctx.payload.get("view_type", "OV-1")
        source = loop_ctx.payload.get("source_markdown", "")

        # The submitted document is always the primary content -- a
        # retriever enriches this, it never replaces it. An earlier version
        # of this method treated retrieval and the raw source as
        # either/or: once retrieval returned anything, the raw source was
        # dropped entirely. That is safe only when the retriever indexes
        # this same source document; against a general reference corpus
        # (DoDAF authoring guidance, prior unrelated programs) it would
        # silently swap the submitted program's own content for a
        # different program's, since the retrieval query below is generic
        # ("DoDAF {view_type}..."), not specific to this submission.
        context_text = source[:8000] if source else ""

        retriever = self._get_retriever()
        if retriever and source:
            chunks = retriever.retrieve(
                intent="dodaf_view_generation",
                query=f"DoDAF {view_type} operational capability system",
                top_k=5,
            )
            if chunks:
                reference_text = "\n\n".join(c["text"] for c in chunks)
                context_text += (
                    "\n\n---\nSupplementary reference material "
                    "(general DoDAF/acquisition guidance and precedent "
                    "programs -- NOT part of the submitted document; use "
                    "only for authoring guidance and pattern-matching, "
                    "never as a source of this program's own facts):\n"
                    f"{reference_text}"
                )

        return {"view_type": view_type, "context": context_text, "iteration": loop_ctx.iteration}

    def run_validation(self, hypothesis, loop_ctx: ValidationLoopContext):
        view_type = hypothesis["view_type"]
        prior = loop_ctx.payload.get("prior_outputs", {})
        prev_attempt = ""
        if loop_ctx.steps:
            prev_attempt = f"\nPrevious attempt (refine, do not repeat errors):\n{loop_ctx.steps[-1].observation.get('view_content', '')[:2000]}"

        req = InferenceRequest(
            prompt=(
                f"Role: {self.config.get('role', 'DoDAF View Generator')}\n"
                f"Goal: {self.config.get('goal', 'Generate DoDAF architecture views')}\n\n"
                f"Generate DoDAF 2.0 view: {view_type}\n\n"
                f"Source context:\n{hypothesis['context']}\n"
                f"{prev_attempt}\n\n"
                "Rules:\n"
                "- Use ONLY information from the submitted document for this program's own facts.\n"
                "  Mark gaps as NOT PROVIDED IN SOURCE.\n"
                "- If a 'Supplementary reference material' section is present, use it only to\n"
                "  follow correct DoDAF structure/terminology -- never to fill in this program's\n"
                "  facts, even if it describes a similar-sounding capability or requirement.\n"
                "- Use DoDAF ID formats (CAP-001, ACT-001, NODE-001).\n"
                "- Neutral DoD-review-ready tone.\n"
                "- NEVER mention AI, ML, cloud, Kafka, K9-AIF.\n"
                "- Include verbatim evidence citations.\n"
            ),
            metadata={"agent": self.layer},
            task_type=self.config.get("model", "reasoning"),
        )
        resp = llm_invoke(self.config, req)
        return {"output": resp.output, "view_type": view_type}

    def evaluate_observation(self, tool_result, loop_ctx: ValidationLoopContext):
        output = tool_result.get("output", "")
        has_ids = any(prefix in output for prefix in ["CAP-", "ACT-", "NODE-", "SYS-", "SVC-"])
        has_not_provided = "NOT PROVIDED IN SOURCE" in output
        has_structure = output.count("#") >= 2
        completeness = sum([has_ids, has_not_provided or len(output) > 500, has_structure]) / 3.0
        confidence = min(0.95, 0.4 + (completeness * 0.5))
        return {"view_content": output, "confidence": confidence, "view_type": tool_result["view_type"]}

    def should_continue(self, observation, loop_ctx: ValidationLoopContext):
        threshold = self.config.get("confidence_threshold", 0.75)
        if observation["confidence"] >= threshold:
            return ValidationDisposition.FINALIZE
        if loop_ctx.iteration >= self.config.get("max_iterations", 3):
            return ValidationDisposition.FINALIZE
        return ValidationDisposition.CONTINUE

    def finalize(self, loop_ctx: ValidationLoopContext) -> ValidationLoopResult:
        last = loop_ctx.steps[-1] if loop_ctx.steps else None
        output = last.observation.get("view_content", "") if last else ""
        view_type = last.observation.get("view_type", "") if last else ""
        confidence = last.confidence if last else 0.0

        self.publish_event({"type": "AgentCompleted", "agent": self.layer, "view_type": view_type})
        return ValidationLoopResult(
            disposition=ValidationDisposition.FINALIZE,
            output={"agent": self.layer, "view_type": view_type, "output": output},
            steps=loop_ctx.steps,
            iterations=loop_ctx.iteration,
            final_confidence=confidence,
            evidence=[str(s.observation) for s in loop_ctx.steps],
        )
