# SPDX-License-Identifier: Apache-2.0

"""Stage 2 — Scope / ICD Needs Analysis Squad."""

from __future__ import annotations

from typing import Any, Dict, Optional

from k9_dow.agents.src.base_dow_agent import BaseDowAgent
from k9_dow.agents.src.project_scope_agent import ProjectScopeAgent
from k9_dow.agents.src.constraint_agent import ConstraintAgent
from k9_dow.agents.src.operational_extractor_agent import OperationalExtractorAgent
from k9_dow.agents.src.capability_extractor_agent import CapabilityExtractorAgent
from k9_dow.agents.src.risk_extractor_agent import RiskExtractorAgent
from k9_dow.agents.src.vocabulary_agent import VocabularyAgent
from k9_dow.agents.src.architecture_analyzer_agent import ArchitectureAnalyzerAgent
from k9_dow.agents.src.requirement_agent import RequirementAgent
from k9_dow.agents.src.summarizer_agent import SummarizerAgent
from k9_dow.agents.src.governance_agent import GovernanceAgent
from k9_dow.messaging.event_publisher import EventPublisher
from k9_dow.persistence.file_repository import FileRepository
from k9_dow.squads.src.base_stage_squad import BaseStageSquad


class Stage2ScopeIcdSquad(BaseStageSquad):

    squad_id = "stage2_scope_icd"
    stage_name = "Scope / ICD Needs Analysis"
    stage_num = 2

    def build_agents(self) -> list[BaseDowAgent]:
        kwargs = {
            "config": self.config,
            "event_publisher": self.event_publisher,
        }
        return [
            ProjectScopeAgent(**kwargs),
            ConstraintAgent(**kwargs),
            OperationalExtractorAgent(**kwargs),
            CapabilityExtractorAgent(**kwargs),
            RiskExtractorAgent(**kwargs),
            VocabularyAgent(**kwargs),
            ArchitectureAnalyzerAgent(**kwargs),
            RequirementAgent(**kwargs),
            SummarizerAgent(**kwargs),
            GovernanceAgent(**kwargs),
        ]
