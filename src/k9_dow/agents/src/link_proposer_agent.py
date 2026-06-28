from __future__ import annotations

from k9_aif_abb.k9_agents.validation import (
    K9ValidationLoopAgent,
    ValidationDisposition,
    ValidationLoopContext,
    ValidationLoopResult,
)
from k9_aif_abb.k9_inference.models.inference_request import InferenceRequest
from k9_aif_abb.k9_utils.llm_invoke import llm_invoke


class LinkProposerAgent(K9ValidationLoopAgent):
    """Proposes trace links between requirements, capability docs, test cases,
    and DoDAF views. Iterates until link confidence reaches threshold.

    4Ds: Augmentation — proposes links, humans approve via HITL.
    Uses K9Retriever to pull relevant chunks from large documents."""

    layer = "DAS LinkProposer"

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
        source = loop_ctx.payload.get("source_markdown", "")
        prior = loop_ctx.payload.get("prior_outputs", {})

        retriever = self._get_retriever()
        if retriever and source:
            chunks = retriever.retrieve(
                intent="trace_link_extraction",
                query="requirements traceability links capability need test case",
                top_k=10,
            )
            context_text = "\n".join(c["text"] for c in chunks)
        else:
            context_text = source[:8000] if source else str(prior)[:8000]

        return {
            "query": "Identify trace links between requirements and artifacts",
            "context": context_text,
            "prior": prior,
            "iteration": loop_ctx.iteration,
        }

    def run_validation(self, hypothesis, loop_ctx: ValidationLoopContext):
        req = InferenceRequest(
            prompt=(
                f"Role: {self.config.get('role', 'Requirements Traceability Analyst')}\n"
                f"Goal: {self.config.get('goal', 'Propose trace links')}\n\n"
                f"Instructions: {self.config.get('instructions', '')}\n\n"
                f"Context:\n{hypothesis['context']}\n\n"
                "Identify trace links: FROM_ID -> RELATIONSHIP -> TO_ID.\n"
                "Valid relationships: DERIVES, DECOMPOSES_TO, VERIFIED_BY, EXPRESSED_IN, "
                "FUNDED_BY, BASELINED_IN, ALLOCATED_TO, DEPENDS_ON.\n"
                "Include confidence (0.0-1.0) and verbatim evidence for each link.\n"
                "Output as structured list."
            ),
            metadata={"agent": self.layer},
            task_type=self.config.get("model", "reasoning"),
        )
        resp = llm_invoke(self.config, req)
        return {"output": resp.output, "model": resp.model_alias}

    def evaluate_observation(self, tool_result, loop_ctx: ValidationLoopContext):
        output = tool_result.get("output", "")
        link_count = output.lower().count("->") + output.lower().count("derives") + output.lower().count("verified_by")
        confidence = min(0.95, 0.5 + (link_count * 0.05))
        return {
            "proposed_links": output,
            "link_count": link_count,
            "confidence": confidence,
        }

    def should_continue(self, observation, loop_ctx: ValidationLoopContext):
        threshold = self.config.get("confidence_threshold", 0.8)
        if observation["confidence"] >= threshold:
            return ValidationDisposition.FINALIZE
        if loop_ctx.iteration >= self.config.get("max_iterations", 3):
            return ValidationDisposition.FINALIZE
        return ValidationDisposition.CONTINUE

    def finalize(self, loop_ctx: ValidationLoopContext) -> ValidationLoopResult:
        last = loop_ctx.steps[-1] if loop_ctx.steps else None
        output = last.observation.get("proposed_links", "") if last else ""
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
