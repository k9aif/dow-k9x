# SPDX-License-Identifier: Apache-2.0
# DoW Architecture Workbench — PrincipalOrchestrator (SBB)
#
# Cascade: DoDAF → HIL Gate #1 → JCIDS (Phase 2) → HIL Gate #2 → SE (Phase 3)

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from k9_aif_abb.k9_core.orchestration.base_orchestrator import BaseOrchestrator

from k9_dow.orchestrators.dodaf_orchestrator import DodafOrchestrator
from k9_dow.routers.dow_document_router import DowDocumentRouter
from k9_dow.agents.src.document_normalization_agent import DocumentNormalizationAgent
from k9_dow.utils.ids import generate_job_id

log = logging.getLogger(__name__)


class PrincipalOrchestrator(BaseOrchestrator):
    """
    Top-level cascade orchestrator for the DoW Architecture Workbench.

    Document → Normalize → Route → DoDAF → [HIL] → JCIDS → [HIL] → SE
    """

    layer = "DoW PrincipalOrchestrator SBB"

    def __init__(self, config: Optional[Dict[str, Any]] = None, **kwargs) -> None:
        super().__init__(config=config or {}, **kwargs)

        self._router = DowDocumentRouter(config=self.config)
        self._normalizer = DocumentNormalizationAgent(config=self.config)
        self._dodaf = DodafOrchestrator(config=self.config)

    def execute_flow(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        job_id = payload.get("job_id") or generate_job_id()
        filename = payload.get("filename", "unknown")
        text = payload.get("text") or payload.get("markdown") or ""

        log.info("[PrincipalOrchestrator] Job %s started — file=%s", job_id, filename)

        # 1. Normalize
        norm_result = self._normalizer.execute({
            "source_markdown": text,
            "metadata": payload.get("metadata", {}),
        })
        normalized_md = norm_result.get("output") or norm_result.get("markdown") or text

        if not normalized_md or not normalized_md.strip():
            return {"job_id": job_id, "status": "failed", "error": "Empty document after normalization"}

        # 2. Route (deterministic)
        routing = self._router.route({
            "job_id": job_id,
            "filename": filename,
            "markdown": normalized_md,
            "document_type": payload.get("document_type", ""),
        })

        route_to = routing.get("route_to", "unknown_pipeline")

        # 3. Execute DoDAF pipeline (Phase 1)
        if route_to == "dodaf_pipeline":
            result = self._dodaf.execute_flow({
                "job_id": job_id,
                "normalized_markdown": normalized_md,
                "routing_decision": routing,
            })
            result["routing"] = routing
            return result

        # Other pipelines — Phase 2/3
        return {
            "job_id": job_id,
            "status": "unsupported_pipeline",
            "route_to": route_to,
            "routing": routing,
            "message": f"Pipeline '{route_to}' not yet implemented. Phase 1 supports DoDAF only.",
        }

    def process_upload(self, filename: str, content: bytes | str) -> Dict[str, Any]:
        """Convenience for API upload handler."""
        job_id = generate_job_id()
        text = content.decode("utf-8", errors="ignore") if isinstance(content, bytes) else content
        return self.execute_flow({"job_id": job_id, "filename": filename, "text": text})

    def resume_after_hil_gate_1(self, job_id: str) -> Dict[str, Any]:
        """Phase 2 — not yet implemented."""
        return {"job_id": job_id, "status": "awaiting_jcids_implementation"}

    def resume_after_hil_gate_2(self, job_id: str) -> Dict[str, Any]:
        """Phase 3 — not yet implemented."""
        return {"job_id": job_id, "status": "awaiting_se_implementation"}
