# SPDX-License-Identifier: Apache-2.0
# K9-AIF Framework
"""MsaOrchestrator: from a validated requirement to Milestone A (process model mca-2026-10).

Two runs, each started by a recorded human approval:

- ``mdd_package`` (after SERVICE-VALIDATION): draft AoA study guidance and study plan, judged
  against the MDD entry criteria (DoDI 5000.85 3.5) → MDD task for the MDA.
- ``msa`` (after MDD): AoA summary, Alternative Systems Review (best practice, SE Guidebook
  3.1) and the proposed acquisition strategy matched to a pathway, judged against the
  Milestone A criteria (DoDI 5000.85 3.7) → MILESTONE-A task.

Replaces the JCIDS-era AcquisitionOrchestrator (PATHWAY-MILESTONE).
"""

from __future__ import annotations

from typing import Any, Dict

from k9_dow.orchestrators.stage_base import PACKAGE_AGENTS, READINESS_AGENTS, ProcessStageOrchestrator


class MsaOrchestrator(ProcessStageOrchestrator):
    layer = "DAS MSA Orchestrator"
    AGENTS = ("AoaStudyPlanAgent", "AoaSummaryAgent", "AlternativeSystemsReviewAgent",
              "AcquisitionStrategyAgent") + READINESS_AGENTS + PACKAGE_AGENTS

    def execute_flow(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        # Ingress: the reviewer's comment is the only new free text; screen it before any agent reads it.
        payload = self.withhold_comment(payload, self.apply_shield(self.decision_text(payload)))
        approved = payload.get("gate_id", "")
        if approved == "SERVICE-VALIDATION":
            return self.run_package(
                payload, run="mdd_package", approved_gate=approved, gate_id="MDD",
                content=("mdd_package_squad.yaml", "MddPackageSquad", "mdd_analysis"),
                prior_from={"requirement": ("gate_readiness", "joint_review")},
                description="Validated requirement with draft AoA study guidance and study plan. The MDA "
                            "decides the phase of entry and the initial review milestone (ADM).")
        if approved == "MDD":
            return self.run_package(
                payload, run="msa", approved_gate=approved, gate_id="MILESTONE-A",
                content=("msa_analysis_squad.yaml", "MsaAnalysisSquad", "msa_analysis"),
                prior_from={"requirement": ("joint_review",), "mdd_package": ("mdd_analysis",)},
                description="Materiel Solution Analysis complete: AoA summary, Alternative Systems Review "
                            "and proposed acquisition strategy. The MDA decides Milestone A (ADM), "
                            "approving the acquisition strategy and its pathway.")
        return {"job_id": payload.get("job_id"), "orchestrator": "MsaOrchestrator", "status": "error",
                "detail": f"MSA runs start after SERVICE-VALIDATION or MDD, not {approved!r}"}
