# SPDX-License-Identifier: Apache-2.0

"""
DoDAF Orchestrator — executes the 6-stage DoDAF pipeline.

Stage 1 → Stage 2 → Stage 3 → Stage 4 → Stage 5 → Stage 6
Sequential for Phase 1. Config option for future parallel after Stage 1.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from k9_aif_abb.k9_core.orchestration.base_orchestrator import BaseOrchestrator

from k9_dow.contracts.events import DowEvent
from k9_dow.contracts.payloads import RoutingDecision, StageExecutionContext
from k9_dow.contracts.stage_results import JobResult, StageResult
from k9_dow.config.settings import settings
from k9_dow.messaging.event_publisher import EventPublisher
from k9_dow.persistence.file_repository import FileRepository
from k9_dow.squads.src.base_stage_squad import BaseStageSquad
from k9_dow.utils.ids import generate_stage_id

log = logging.getLogger(__name__)


_STAGE_SEQUENCE = [
    (1, "Fit-for-Purpose / Intended Use", "stage1_fit_for_purpose"),
    (2, "Scope / ICD Needs Analysis", "stage2_scope_icd"),
    (3, "Required Data Identification", "stage3_data_requirements"),
    (4, "Architecture Data Correlation", "stage4_architecture_correlation"),
    (5, "Architecture Analysis", "stage5_architecture_analysis"),
    (6, "Presentation and Reporting", "stage6_presentation"),
]


class DodafOrchestrator(BaseOrchestrator):
    """
    DoDAF Pipeline Orchestrator (SBB).

    Executes Stages 1-6 sequentially. Each stage is a BaseStageSquad
    that sequences its own agents.
    """

    layer = "DoDAF Orchestrator SBB"

    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        monitor=None,
        event_publisher: Optional[EventPublisher] = None,
        file_repo: Optional[FileRepository] = None,
    ):
        super().__init__(config=config or {}, monitor=monitor)
        self.event_publisher = event_publisher
        self.file_repo = file_repo or FileRepository()
        self._squads = self._build_squads()

    def _build_squads(self) -> dict[str, BaseStageSquad]:
        from k9_dow.squads.src.stage1_fit_for_purpose_squad import Stage1FitForPurposeSquad
        from k9_dow.squads.src.stage2_scope_icd_squad import Stage2ScopeIcdSquad
        from k9_dow.squads.src.stage3_data_requirements_squad import Stage3DataRequirementsSquad
        from k9_dow.squads.src.stage4_architecture_correlation_squad import Stage4ArchitectureCorrelationSquad
        from k9_dow.squads.src.stage5_architecture_analysis_squad import Stage5ArchitectureAnalysisSquad
        from k9_dow.squads.src.stage6_presentation_squad import Stage6PresentationSquad

        kwargs = {
            "config": self.config,
            "event_publisher": self.event_publisher,
            "file_repo": self.file_repo,
        }

        return {
            "stage1_fit_for_purpose": Stage1FitForPurposeSquad(**kwargs),
            "stage2_scope_icd": Stage2ScopeIcdSquad(**kwargs),
            "stage3_data_requirements": Stage3DataRequirementsSquad(**kwargs),
            "stage4_architecture_correlation": Stage4ArchitectureCorrelationSquad(**kwargs),
            "stage5_architecture_analysis": Stage5ArchitectureAnalysisSquad(**kwargs),
            "stage6_presentation": Stage6PresentationSquad(**kwargs),
        }

    def execute_flow(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        job_id = payload.get("job_id", "")
        routing = payload.get("routing_decision")
        if routing and isinstance(routing, dict):
            routing = RoutingDecision(**routing)

        normalized_md = payload.get("normalized_markdown", "")
        route = payload.get("route", "dodaf_pipeline")

        self._emit("PipelineStarted", job_id, message="DoDAF pipeline started")
        log.info("[DodafOrchestrator] Starting DoDAF pipeline for job=%s", job_id)

        job_result = JobResult(
            job_id=job_id,
            route=route,
            classification=routing.classification if routing else "DODAF",
        )

        accumulated_outputs: dict[str, str] = {}

        for stage_num, stage_name, squad_key in _STAGE_SEQUENCE:
            squad = self._squads.get(squad_key)
            if squad is None:
                log.info(
                    "[DodafOrchestrator] Stage %d (%s) not yet implemented — skipping",
                    stage_num, stage_name,
                )
                continue

            stage_id = generate_stage_id(stage_num, stage_name)

            context = StageExecutionContext(
                job_id=job_id,
                route=route,
                stage_id=stage_id,
                stage_name=stage_name,
                source_document=normalized_md,
                normalized_markdown=normalized_md,
                prior_stage_outputs=accumulated_outputs,
                routing_decision=routing,
            )

            stage_result = squad.execute(context)
            job_result.stage_results.append(stage_result)

            if stage_result.markdown_report:
                accumulated_outputs[f"stage{stage_num}"] = stage_result.markdown_report

            if stage_result.status in ("failed", "blocked"):
                log.warning(
                    "[DodafOrchestrator] Stage %d %s — stopping pipeline",
                    stage_num, stage_result.status,
                )
                job_result.status = stage_result.status
                break

            if (
                stage_num == 2
                and settings.REQUIRE_HIL_AFTER_STAGE2
            ):
                log.info("[DodafOrchestrator] HIL gate after Stage 2 — pausing")
                job_result.status = "needs_human_review"
                break

        if job_result.status == "running":
            job_result.status = "completed"

        self._persist_job(job_result)
        self._emit(
            "PipelineCompleted" if job_result.status == "completed" else "PipelineFailed",
            job_id,
            message=f"DoDAF pipeline {job_result.status}",
        )

        log.info(
            "[DodafOrchestrator] DoDAF pipeline %s for job=%s (%d stages executed)",
            job_result.status, job_id, len(job_result.stage_results),
        )

        return job_result.model_dump()

    def _persist_job(self, job_result: JobResult) -> None:
        if not self.file_repo:
            return
        try:
            self.file_repo.save_artifact_index(job_result.job_id)
            self.file_repo.save_json(
                job_result.job_id,
                "routing_manifest.json",
                job_result.model_dump(),
            )
        except Exception as exc:
            log.warning("[DodafOrchestrator] Job persistence failed: %s", exc)

    def _emit(self, event_type: str, job_id: str, message: str = "") -> None:
        if not self.event_publisher:
            return
        self.event_publisher.publish(DowEvent(
            event_type=event_type,
            job_id=job_id,
            route="dodaf_pipeline",
            message=message or event_type,
        ))
