# SPDX-License-Identifier: Apache-2.0

"""Stage 1 — Fit-for-Purpose / Intended Use Squad."""

from __future__ import annotations

from typing import Any, Dict, Optional

from k9_dow.agents.src.base_dow_agent import BaseDowAgent
from k9_dow.agents.src.validation_agent import ValidationAgent
from k9_dow.agents.src.stakeholder_extractor_agent import StakeholderExtractorAgent
from k9_dow.agents.src.pain_point_extractor_agent import PainPointExtractorAgent
from k9_dow.agents.src.objective_extractor_agent import ObjectiveExtractorAgent
from k9_dow.agents.src.mission_assessment_agent import MissionAssessmentAgent
from k9_dow.agents.src.f2p_intent_agent import F2PIntentAgent
from k9_dow.agents.src.summarizer_agent import SummarizerAgent
from k9_dow.agents.src.governance_agent import GovernanceAgent
from k9_dow.messaging.event_publisher import EventPublisher
from k9_dow.persistence.file_repository import FileRepository
from k9_dow.squads.src.base_stage_squad import BaseStageSquad


class Stage1FitForPurposeSquad(BaseStageSquad):

    squad_id = "stage1_fit_for_purpose"
    stage_name = "Fit-for-Purpose / Intended Use"
    stage_num = 1

    def build_agents(self) -> list[BaseDowAgent]:
        kwargs = {
            "config": self.config,
            "event_publisher": self.event_publisher,
        }
        return [
            ValidationAgent(**kwargs),
            StakeholderExtractorAgent(**kwargs),
            PainPointExtractorAgent(**kwargs),
            ObjectiveExtractorAgent(**kwargs),
            MissionAssessmentAgent(**kwargs),
            F2PIntentAgent(**kwargs),
            SummarizerAgent(**kwargs),
            GovernanceAgent(**kwargs),
        ]
