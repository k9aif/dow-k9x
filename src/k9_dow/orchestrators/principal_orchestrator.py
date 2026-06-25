# SPDX-License-Identifier: Apache-2.0

"""
PrincipalOrchestrator — top-level orchestrator that receives a routed
job event and delegates to the correct pipeline orchestrator.

Phase 1: only DoDAF pipeline is implemented.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from k9_aif_abb.k9_core.orchestration.base_orchestrator import BaseOrchestrator

from k9_dow.contracts.events import DowEvent
from k9_dow.contracts.payloads import DocumentInput, RoutingDecision
from k9_dow.contracts.stage_results import JobResult
from k9_dow.messaging.event_publisher import EventPublisher
from k9_dow.persistence.file_repository import FileRepository
from k9_dow.orchestrators.dodaf_orchestrator import DodafOrchestrator
from k9_dow.routers.dow_document_router import DowDocumentRouter
from k9_dow.agents.src.document_normalization_agent import DocumentNormalizationAgent
from k9_dow.utils.ids import generate_job_id

log = logging.getLogger(__name__)


class PrincipalOrchestrator(BaseOrchestrator):
    """
    Top-level orchestrator for the DoW Architecture Workbench.

    Responsibilities:
      1. Receive uploaded document
      2. Normalize to markdown
      3. Route to correct pipeline
      4. Execute pipeline orchestrator
      5. Return job result
    """

    layer = "DoW PrincipalOrchestrator SBB"

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

        self._router = DowDocumentRouter(
            config=self.config,
            event_publisher=self.event_publisher,
        )

        self._normalizer = DocumentNormalizationAgent(
            config=self.config,
            event_publisher=self.event_publisher,
        )

        self._pipelines = {
            "dodaf_pipeline": DodafOrchestrator(
                config=self.config,
                event_publisher=self.event_publisher,
                file_repo=self.file_repo,
            ),
        }

    def execute_flow(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        job_id = payload.get("job_id") or generate_job_id()
        filename = payload.get("filename", "unknown")
        text = payload.get("text") or payload.get("markdown") or ""
        raw_path = payload.get("raw_path")

        log.info("[PrincipalOrchestrator] Job %s started — file=%s", job_id, filename)
        self._emit("DocumentUploaded", job_id, message=f"Document uploaded: {filename}")

        # ── 1. Normalize ──────────────────────────────────────────────
        norm_payload = {
            "job_id": job_id,
            "stage_id": "stage0_normalization",
            "agent_name": "DocumentNormalizationAgent",
            "source_markdown": text,
            "metadata": {"raw_path": raw_path} if raw_path else {},
        }
        norm_result = self._normalizer.execute(norm_payload)
        normalized_md = norm_result.get("markdown", text)

        if not normalized_md or not normalized_md.strip():
            log.error("[PrincipalOrchestrator] Normalization produced empty text")
            return JobResult(
                job_id=job_id,
                route="unknown",
                classification="UNKNOWN",
                status="failed",
            ).model_dump()

        self._emit("DocumentNormalized", job_id)

        if self.file_repo:
            self.file_repo.save_markdown(job_id, "normalized_input.md", normalized_md)

        # ── 2. Route ──────────────────────────────────────────────────
        doc_input = DocumentInput(
            job_id=job_id,
            filename=filename,
            content_type="text/markdown",
            markdown=normalized_md,
        )
        routing_raw = self._router.route(doc_input.model_dump())
        routing = RoutingDecision(**routing_raw)

        if self.file_repo:
            self.file_repo.save_json(job_id, "routing_manifest.json", routing.model_dump())

        # ── 3. Execute pipeline ───────────────────────────────────────
        pipeline = self._pipelines.get(routing.route_to)
        if pipeline is None:
            log.warning(
                "[PrincipalOrchestrator] No pipeline for route=%s — Phase 1 supports dodaf only",
                routing.route_to,
            )
            return JobResult(
                job_id=job_id,
                route=routing.route_to,
                classification=routing.classification,
                status="failed",
                artifact_index={"routing_manifest": "routing_manifest.json"},
            ).model_dump()

        pipeline_payload = {
            "job_id": job_id,
            "route": routing.route_to,
            "normalized_markdown": normalized_md,
            "routing_decision": routing.model_dump(),
        }

        result = pipeline.execute_flow(pipeline_payload)

        log.info(
            "[PrincipalOrchestrator] Job %s completed — route=%s status=%s",
            job_id, routing.route_to, result.get("status", "unknown"),
        )
        return result

    def process_upload(
        self,
        filename: str,
        content: bytes | str,
        raw_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Convenience method for API upload handler."""
        job_id = generate_job_id()

        if self.file_repo and isinstance(content, bytes):
            self.file_repo.save_input(job_id, filename, content)

        text = content.decode("utf-8", errors="ignore") if isinstance(content, bytes) else content

        return self.execute_flow({
            "job_id": job_id,
            "filename": filename,
            "text": text,
            "raw_path": raw_path,
        })

    def _emit(self, event_type: str, job_id: str, message: str = "") -> None:
        if not self.event_publisher:
            return
        self.event_publisher.publish(DowEvent(
            event_type=event_type,
            job_id=job_id,
            message=message or event_type,
        ))
