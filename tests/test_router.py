# SPDX-License-Identifier: Apache-2.0
# Tests for DowDocumentRouter and agents — all use K9-AIF ABBs directly.

import pytest

from k9_dow.routers.dow_document_router import DowDocumentRouter


@pytest.fixture
def router():
    return DowDocumentRouter(config={})


def _doc(job_id: str, text: str, doc_type: str = "") -> dict:
    return {"job_id": job_id, "filename": "test.md", "markdown": text, "document_type": doc_type}


class TestDeterministicRouting:

    def test_dodaf_keyword(self, router):
        result = router.route(_doc("J001", "system architecture and mission capability"))
        assert result["classification"] == "DODAF"
        assert result["route_to"] == "dodaf_pipeline"

    def test_business_meeting_notes(self, router):
        result = router.route(_doc("J002", "call report from industry day meeting with contracting officer"))
        assert result["classification"] == "BD"
        assert result["route_to"] == "business_pipeline"

    def test_jcids_requirements(self, router):
        result = router.route(_doc("J003", "initial capabilities document capability gap mission need"))
        assert result["classification"] == "JCIDS"
        assert result["route_to"] == "jcids_pipeline"

    def test_se_document(self, router):
        result = router.route(_doc("J004", "systems engineering functional analysis design synthesis verification"))
        assert result["classification"] == "SE"
        assert result["route_to"] == "se_pipeline"

    def test_unknown_fallback(self, router):
        result = router.route(_doc("J005", "random text no domain keywords at all filler"))
        assert result["route_to"] in ("unknown_pipeline", "business_pipeline")

    def test_user_selected_type_overrides(self, router):
        result = router.route(_doc("J006", "random text", doc_type="dodaf"))
        assert result["classification"] == "DODAF"
        assert result["route_to"] == "dodaf_pipeline"
        assert result["confidence"] == 1.0

    def test_matched_rules_populated(self, router):
        result = router.route(_doc("J007", "architecture and capability"))
        assert len(result.get("matched_rules", [])) > 0


class TestValidationAgent:

    def test_short_document_flagged(self):
        from k9_dow.agents.src.validation_agent import ValidationAgent
        agent = ValidationAgent(config={})
        result = agent.execute({"source_markdown": "Too short."})
        assert result["valid"] is False

    def test_sufficient_document_passes(self):
        from k9_dow.agents.src.validation_agent import ValidationAgent
        agent = ValidationAgent(config={})
        text = "# Architecture Document\n\n" + "This is a substantial paragraph. " * 50
        result = agent.execute({"source_markdown": text})
        assert result["valid"] is True


class TestDocumentNormalization:

    def test_passthrough_markdown(self):
        from k9_dow.agents.src.document_normalization_agent import DocumentNormalizationAgent
        agent = DocumentNormalizationAgent(config={})
        result = agent.execute({"source_markdown": "# Hello\n\nWorld"})
        assert result.get("output") or result.get("markdown")

    def test_empty_input(self):
        from k9_dow.agents.src.document_normalization_agent import DocumentNormalizationAgent
        agent = DocumentNormalizationAgent(config={})
        result = agent.execute({"source_markdown": ""})
        assert "error" in str(result).lower() or result.get("output", "") == ""
