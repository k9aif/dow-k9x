from __future__ import annotations

from k9_aif_abb.k9_core.agent.base_agent import BaseAgent
from k9_aif_abb.k9_inference.models.inference_request import InferenceRequest
from k9_aif_abb.k9_utils.llm_invoke import llm_invoke


class PackageBuilderAgent(BaseAgent):
    """Assembles the final review-ready artifact package for the HITL gate.
    Includes provenance: which agent, which model, which source records,
    which gate cleared it."""

    layer = "DAS PackageBuilder"

    def __init__(self, config=None, monitor=None, **kwargs):
        super().__init__(config or {}, monitor=monitor, **kwargs)

    def execute(self, payload: dict) -> dict:
        prior = payload.get("prior_outputs", {})
        gate_id = payload.get("gate_id", "")

        req = InferenceRequest(
            prompt=(
                f"Role: {self.config.get('role', 'Artifact Package Builder')}\n"
                f"Goal: {self.config.get('goal', 'Assemble review-ready artifact package')}\n\n"
                f"Instructions: {self.config.get('instructions', '')}\n\n"
                f"Gate: {gate_id}\n"
                f"Artifacts and assessments:\n{prior}\n\n"
                "Assemble the final package:\n"
                "1. Executive summary of readiness state\n"
                "2. Evidence manifest with provenance\n"
                "3. Gap report (if any gaps exist)\n"
                "4. Traceability coverage score\n"
                "5. Drift alerts (if any)\n"
                "6. Recommendation (but NOT a decision — that's for the human)\n\n"
                "Output as structured package ready for decision authority review."
            ),
            metadata={"agent": self.layer},
            task_type=self.config.get("model", "reasoning"),
        )
        resp = llm_invoke(self.config, req)

        result = {"agent": self.layer, "output": resp.output}

        if self.config.get("emit_icd_docx", True):
            try:
                from k9_dow.reporting.icd_report_builder import IcdReportBuilder
                builder = IcdReportBuilder(config=self.config)
                metadata = payload.get("icd_metadata", {})
                all_outputs = {**prior, "review_package": {"output": resp.output}}
                uri = builder.build_and_store(
                    prior_outputs=all_outputs,
                    metadata=metadata,
                    config=self.config,
                )
                result["icd_docx_uri"] = uri
                self.publish_event({"type": "ArtifactGenerated", "artifact": "ICD.docx", "uri": uri})
            except ImportError:
                pass
            except Exception as exc:
                result["icd_docx_error"] = str(exc)

        self.publish_event({"type": "AgentCompleted", "agent": self.layer})
        return result
