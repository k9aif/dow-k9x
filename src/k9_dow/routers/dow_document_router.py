# SPDX-License-Identifier: Apache-2.0
# DoW Architecture Workbench — DowDocumentRouter (SBB)
#
# Deterministic routing: user selects document type in UI = intent.
# Router maps selection → pipeline. No LLM classification needed.

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from k9_aif_abb.k9_core.router.base_router import BaseRouter

from k9_dow.config.settings import settings

log = logging.getLogger(__name__)


class DowDocumentRouter(BaseRouter):
    """
    DoW Document Router (SBB).

    Extends BaseRouter. Routes documents into the correct pipeline
    based on deterministic keyword matching from routing_rules.yaml.
    """

    layer = "DoW DocumentRouter SBB"

    def __init__(self, config: Optional[Dict[str, Any]] = None, **kwargs) -> None:
        super().__init__(config=config or {}, **kwargs)
        self._rules = settings.routing_rules()

    def route(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        job_id = payload.get("job_id", "")
        text = (payload.get("markdown") or payload.get("text") or "").lower()
        doc_type = payload.get("document_type", "")

        if doc_type:
            decision = self._route_by_type(job_id, doc_type)
            if decision:
                return decision

        decision = self._deterministic_route(job_id, text)
        if decision:
            return decision

        return self._default_decision(job_id)

    def _route_by_type(self, job_id: str, doc_type: str) -> Optional[Dict[str, Any]]:
        """Route by explicit document type selection from UI."""
        type_map = {
            "dodaf": ("DODAF", "dodaf_pipeline"),
            "jcids": ("JCIDS", "jcids_pipeline"),
            "se": ("SE", "se_pipeline"),
            "business": ("BD", "business_pipeline"),
        }
        match = type_map.get(doc_type.lower())
        if not match:
            return None

        classification, route_to = match
        return {
            "job_id": job_id,
            "classification": classification,
            "document_type": doc_type,
            "route_to": route_to,
            "confidence": 1.0,
            "rationale": f"User selected document type: {doc_type}",
            "matched_rules": ["user_selection"],
        }

    def _deterministic_route(self, job_id: str, text: str) -> Optional[Dict[str, Any]]:
        patterns = self._rules.get("patterns", [])
        if not patterns:
            return None

        best_match = None
        best_score = 0
        matched_rules = []

        for pattern in patterns:
            keywords = pattern.get("contains_any", [])
            hits = sum(1 for kw in keywords if kw.lower() in text)
            if hits > 0:
                matched_rules.append(pattern["name"])
                if hits > best_score:
                    best_score = hits
                    best_match = pattern

        if best_match is None:
            return None

        return {
            "job_id": job_id,
            "classification": best_match.get("classification", "UNKNOWN"),
            "document_type": best_match.get("document_type", "unknown"),
            "route_to": best_match.get("route_to", "unknown_pipeline"),
            "dodaf_eligible": best_match.get("dodaf_eligible", False),
            "jcids_eligible": best_match.get("jcids_eligible", False),
            "se_eligible": best_match.get("se_eligible", False),
            "recommended_stages": best_match.get("recommended_stages", []),
            "confidence": min(1.0, best_score / 3.0),
            "rationale": f"Deterministic match: {best_match['name']} ({best_score} keyword hits)",
            "matched_rules": matched_rules,
        }

    def _default_decision(self, job_id: str) -> Dict[str, Any]:
        defaults = self._rules.get("defaults", {}).get("unknown", {})
        return {
            "job_id": job_id,
            "classification": defaults.get("classification", "UNKNOWN"),
            "document_type": defaults.get("document_type", "unknown"),
            "route_to": defaults.get("route_to", "unknown_pipeline"),
            "confidence": 0.0,
            "rationale": "No match — defaulting to unknown pipeline",
        }
