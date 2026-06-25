# SPDX-License-Identifier: Apache-2.0

"""
DowDocumentRouter — K9-AIF BaseRouter implementation for document routing.

Routing strategy:
  1. Deterministic keyword matching from routing_rules.yaml (first match wins)
  2. If multiple matches, score by hit count and pick highest
  3. If no match, call RoutingClassifierAgent for LLM-based classification
  4. Returns RoutingDecision with classification, route, confidence, rationale
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

import yaml

from k9_aif_abb.k9_core.router.base_router import BaseRouter

from k9_dow.config.settings import settings
from k9_dow.contracts.events import DowEvent
from k9_dow.contracts.payloads import DocumentInput, RoutingDecision
from k9_dow.messaging.event_publisher import EventPublisher

log = logging.getLogger(__name__)


class DowDocumentRouter(BaseRouter):
    """
    DoW Document Router (SBB).

    Extends BaseRouter. Routes uploaded documents into the correct
    analysis pipeline: dodaf_pipeline, jcids_pipeline, se_pipeline,
    business_pipeline, or unknown_pipeline.
    """

    layer = "DoW DocumentRouter SBB"

    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        monitor=None,
        message_bus=None,
        governance=None,
        event_publisher: Optional[EventPublisher] = None,
        routing_classifier=None,
    ):
        super().__init__(
            config=config,
            monitor=monitor,
            message_bus=message_bus,
            governance=governance,
        )
        self._event_publisher = event_publisher
        self._routing_classifier = routing_classifier
        self._rules = self._load_rules()

    def _load_rules(self) -> dict:
        rules = settings.routing_rules()
        if not rules:
            log.warning("[DowRouter] No routing rules loaded — all docs route to unknown")
        return rules

    def route(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        doc = DocumentInput(**payload) if isinstance(payload, dict) else payload
        text = (doc.markdown or doc.text or "").lower()

        self._emit("RoutingStarted", doc.job_id)

        decision = self._deterministic_route(doc.job_id, text)

        if decision is None and self._routing_classifier:
            decision = self._llm_route(doc)

        if decision is None:
            decision = self._default_decision(doc.job_id)

        self._emit(
            "RoutingCompleted", doc.job_id,
            message=f"Routed to {decision.route_to} ({decision.classification})",
        )

        log.info(
            "[DowRouter] job=%s → %s (classification=%s, confidence=%.2f)",
            doc.job_id, decision.route_to, decision.classification, decision.confidence,
        )
        return decision.model_dump()

    def route_document(self, doc: DocumentInput) -> RoutingDecision:
        raw = self.route(doc.model_dump())
        return RoutingDecision(**raw)

    # ── Deterministic routing ─────────────────────────────────────────────

    def _deterministic_route(self, job_id: str, text: str) -> Optional[RoutingDecision]:
        patterns = self._rules.get("patterns", [])
        if not patterns:
            return None

        best_match = None
        best_score = 0
        matched_rules: list[str] = []

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

        return RoutingDecision(
            job_id=job_id,
            classification=best_match.get("classification", "UNKNOWN"),
            document_type=best_match.get("document_type", "unknown"),
            route_to=best_match.get("route_to", "unknown_pipeline"),
            dodaf_eligible=best_match.get("dodaf_eligible", False),
            jcids_eligible=best_match.get("jcids_eligible", False),
            se_eligible=best_match.get("se_eligible", False),
            recommended_stages=best_match.get("recommended_stages", []),
            confidence=min(1.0, best_score / 3.0),
            rationale=f"Deterministic match: {best_match['name']} ({best_score} keyword hits)",
            matched_rules=matched_rules,
        )

    # ── LLM fallback routing ─────────────────────────────────────────────

    def _llm_route(self, doc: DocumentInput) -> Optional[RoutingDecision]:
        try:
            from k9_dow.contracts.payloads import DowAgentPayload
            payload = DowAgentPayload(
                job_id=doc.job_id,
                stage_id="stage0_routing",
                agent_name="RoutingClassifierAgent",
                source_markdown=doc.markdown or doc.text or "",
            )
            raw = self._routing_classifier.execute(payload.model_dump())
            data = raw.get("json_data", {})
            if not data:
                return None

            route_map = {
                "BD": "business_pipeline",
                "DODAF": "dodaf_pipeline",
                "JCIDS": "jcids_pipeline",
                "SE": "se_pipeline",
            }
            classification = data.get("classification", "UNKNOWN").upper()

            return RoutingDecision(
                job_id=doc.job_id,
                classification=classification,
                document_type=data.get("document_type", "unknown"),
                route_to=route_map.get(classification, "unknown_pipeline"),
                dodaf_eligible=data.get("dodaf_eligible", False),
                jcids_eligible=data.get("jcids_eligible", False),
                se_eligible=data.get("se_eligible", False),
                recommended_stages=data.get("recommended_stages", []),
                confidence=float(data.get("confidence", 0.5)),
                rationale=data.get("rationale", "LLM classification"),
                matched_rules=["llm_classifier"],
            )
        except Exception as exc:
            log.warning("[DowRouter] LLM routing failed: %s", exc)
            return None

    # ── Default / unknown ─────────────────────────────────────────────────

    def _default_decision(self, job_id: str) -> RoutingDecision:
        defaults = self._rules.get("defaults", {}).get("unknown", {})
        return RoutingDecision(
            job_id=job_id,
            classification=defaults.get("classification", "UNKNOWN"),
            document_type=defaults.get("document_type", "unknown"),
            route_to=defaults.get("route_to", "unknown_pipeline"),
            dodaf_eligible=defaults.get("dodaf_eligible", False),
            jcids_eligible=defaults.get("jcids_eligible", False),
            se_eligible=defaults.get("se_eligible", False),
            recommended_stages=defaults.get("recommended_stages", []),
            confidence=0.0,
            rationale="No deterministic or LLM match — defaulting to unknown pipeline",
        )

    # ── Events ────────────────────────────────────────────────────────────

    def _emit(self, event_type: str, job_id: str, message: str = "") -> None:
        if not self._event_publisher:
            return
        self._event_publisher.publish(DowEvent(
            event_type=event_type,
            job_id=job_id,
            message=message or event_type,
        ))
