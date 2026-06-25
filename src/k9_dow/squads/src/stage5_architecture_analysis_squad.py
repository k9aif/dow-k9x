# SPDX-License-Identifier: Apache-2.0

"""Stage 5 — Architecture Analysis Squad."""

from __future__ import annotations

from typing import Any, Dict, Optional

from k9_dow.agents.src.base_dow_agent import BaseDowAgent
from k9_dow.agents.src.validation_agent import ValidationAgent
from k9_dow.agents.src.verification_agent import VerificationAgent
from k9_dow.agents.src.architecture_analyzer_agent import ArchitectureAnalyzerAgent
from k9_dow.agents.src.capability_analyzer_agent import CapabilityAnalyzerAgent
from k9_dow.agents.src.operational_analyzer_agent import OperationalAnalyzerAgent
from k9_dow.agents.src.risk_extractor_agent import RiskExtractorAgent
from k9_dow.agents.src.action_item_agent import ActionItemAgent
from k9_dow.agents.src.requirement_agent import RequirementAgent
from k9_dow.agents.src.summarizer_agent import SummarizerAgent
from k9_dow.agents.src.governance_agent import GovernanceAgent
from k9_dow.messaging.event_publisher import EventPublisher
from k9_dow.persistence.file_repository import FileRepository
from k9_dow.squads.src.base_stage_squad import BaseStageSquad


class Stage5ArchitectureAnalysisSquad(BaseStageSquad):

    squad_id = "stage5_architecture_analysis"
    stage_name = "Architecture Analysis"
    stage_num = 5

    def build_agents(self) -> list[BaseDowAgent]:
        kwargs = {
            "config": self.config,
            "event_publisher": self.event_publisher,
        }
        return [
            ValidationAgent(**kwargs),
            VerificationAgent(**kwargs),
            ArchitectureAnalyzerAgent(**kwargs),
            CapabilityAnalyzerAgent(**kwargs),
            OperationalAnalyzerAgent(**kwargs),
            RiskExtractorAgent(**kwargs),
            ActionItemAgent(**kwargs),
            RequirementAgent(**kwargs),
            SummarizerAgent(**kwargs),
            GovernanceAgent(**kwargs),
        ]
