# SPDX-License-Identifier: Apache-2.0

"""Tests for DowDocumentRouter — deterministic routing."""

import pytest

from k9_dow.routers.dow_document_router import DowDocumentRouter
from k9_dow.contracts.payloads import DocumentInput, RoutingDecision
from k9_dow.messaging.event_publisher import InMemoryEventPublisher


@pytest.fixture
def router():
    pub = InMemoryEventPublisher()
    return DowDocumentRouter(config={}, event_publisher=pub)


def _doc(job_id: str, text: str) -> dict:
    return DocumentInput(
        job_id=job_id,
        filename="test.md",
        content_type="text/markdown",
        markdown=text,
    ).model_dump()


class TestDeterministicRouting:

    def test_dodaf_architecture_keyword(self, router):
        result = router.route(_doc("J001", "This document describes the system architecture and mission capability."))
        decision = RoutingDecision(**result)
        assert decision.classification == "DODAF"
        assert decision.route_to == "dodaf_pipeline"
        assert decision.confidence > 0

    def test_business_meeting_notes(self, router):
        result = router.route(_doc("J002", "Call report from the industry day meeting with contracting officer."))
        decision = RoutingDecision(**result)
        assert decision.classification == "BD"
        assert decision.route_to == "business_pipeline"

    def test_jcids_requirements(self, router):
        result = router.route(_doc("J003", "Initial capabilities document addressing capability gap and mission need statement."))
        decision = RoutingDecision(**result)
        assert decision.classification == "JCIDS"
        assert decision.route_to == "jcids_pipeline"

    def test_se_document(self, router):
        result = router.route(_doc("J004", "Systems engineering functional analysis and design synthesis verification."))
        decision = RoutingDecision(**result)
        assert decision.classification == "SE"
        assert decision.route_to == "se_pipeline"

    def test_unknown_fallback(self, router):
        result = router.route(_doc("J005", "Random text with no domain keywords at all. Just some filler."))
        decision = RoutingDecision(**result)
        assert decision.route_to in ("unknown_pipeline", "business_pipeline")

    def test_multiple_matches_picks_highest_score(self, router):
        result = router.route(_doc(
            "J006",
            "architecture mission capability operational system description data flow interfaces conops dodaf"
        ))
        decision = RoutingDecision(**result)
        assert decision.classification == "DODAF"
        assert decision.confidence > 0.5

    def test_routing_decision_has_matched_rules(self, router):
        result = router.route(_doc("J007", "This is about architecture and capability."))
        decision = RoutingDecision(**result)
        assert len(decision.matched_rules) > 0


class TestValidationAgent:

    def test_short_document_flagged(self):
        from k9_dow.agents.src.validation_agent import ValidationAgent
        agent = ValidationAgent(config={})
        result = agent.execute({
            "job_id": "J010",
            "stage_id": "stage0",
            "agent_name": "ValidationAgent",
            "source_markdown": "Too short.",
        })
        assert result["json_data"]["valid"] is False

    def test_sufficient_document_passes(self):
        from k9_dow.agents.src.validation_agent import ValidationAgent
        agent = ValidationAgent(config={})
        text = "# Architecture Document\n\n" + "This is a substantial paragraph. " * 50
        result = agent.execute({
            "job_id": "J011",
            "stage_id": "stage0",
            "agent_name": "ValidationAgent",
            "source_markdown": text,
        })
        assert result["json_data"]["valid"] is True


class TestDocumentNormalization:

    def test_passthrough_markdown(self):
        from k9_dow.agents.src.document_normalization_agent import DocumentNormalizationAgent
        agent = DocumentNormalizationAgent(config={})
        result = agent.execute({
            "job_id": "J020",
            "stage_id": "stage0",
            "agent_name": "DocumentNormalizationAgent",
            "source_markdown": "# Hello\n\nWorld",
        })
        assert result["status"] == "completed"
        assert result["markdown"] == "# Hello\n\nWorld"

    def test_empty_input_fails(self):
        from k9_dow.agents.src.document_normalization_agent import DocumentNormalizationAgent
        agent = DocumentNormalizationAgent(config={})
        result = agent.execute({
            "job_id": "J021",
            "stage_id": "stage0",
            "agent_name": "DocumentNormalizationAgent",
            "source_markdown": "",
            "metadata": {},
        })
        assert result["status"] == "failed"
