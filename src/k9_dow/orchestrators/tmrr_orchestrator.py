# SPDX-License-Identifier: Apache-2.0
# K9-AIF Framework
"""TmrrOrchestrator: Technology Maturation and Risk Reduction up to the System Requirements
Review (process model mca-2026-10).

Started by a recorded MILESTONE-A approval: drafts the system requirements and their
traceability, judged against the SRR criteria (SE Guidebook 3.2) → SE-REVIEW-SRR task for
the Service-appointed technical review chair. An SRR approval ends the built flow; SFR, PDR,
CDD-equivalent validation, the Development RFP Release and Milestone B are designed only
(process_model.yaml ``designed``).

Replaces the JCIDS-era SeOrchestrator demonstration endpoint.
"""

from __future__ import annotations

from typing import Any, Dict

from k9_dow.orchestrators.stage_base import PACKAGE_AGENTS, READINESS_AGENTS, ProcessStageOrchestrator


class TmrrOrchestrator(ProcessStageOrchestrator):
    layer = "DAS TMRR Orchestrator"
    AGENTS = ("SystemRequirementsAgent",) + READINESS_AGENTS + PACKAGE_AGENTS

    def execute_flow(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        # Ingress: the reviewer's comment is the only new free text; screen it before any agent reads it.
        payload = self.withhold_comment(payload, self.apply_shield(self.decision_text(payload)))
        approved = payload.get("gate_id", "")
        if approved != "MILESTONE-A":
            return {"job_id": payload.get("job_id"), "orchestrator": "TmrrOrchestrator", "status": "error",
                    "detail": f"TMRR starts after MILESTONE-A, not {approved!r}"}
        return self.run_package(
            payload, run="tmrr", approved_gate=approved, gate_id="SE-REVIEW-SRR",
            content=("srr_package_squad.yaml", "SrrPackageSquad", "srr_analysis"),
            prior_from={"msa": ("msa_analysis",), "requirement": ("joint_review",)},
            description="System requirements drafted from the requirement document and the Milestone A "
                        "package, judged against the SRR criteria. The technical review chair decides "
                        "whether the requirements are ready for initial system design.")
