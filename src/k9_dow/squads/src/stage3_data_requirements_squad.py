# SPDX-License-Identifier: Apache-2.0

"""Stage 3 — Required Data Identification Squad."""

from __future__ import annotations

from typing import Any, Dict, Optional

from k9_dow.agents.src.base_dow_agent import BaseDowAgent
from k9_dow.agents.src.data_requirements_agent import DataRequirementsAgent
from k9_dow.agents.src.capability_extractor_agent import CapabilityExtractorAgent
from k9_dow.agents.src.dm2_extractor_agent import DM2ExtractorAgent
from k9_dow.agents.src.system_service_extractor_agent import SystemServiceExtractorAgent
from k9_dow.agents.src.system_view_agent import SystemViewAgent
from k9_dow.agents.src.summarizer_agent import SummarizerAgent
from k9_dow.agents.src.governance_agent import GovernanceAgent
from k9_dow.messaging.event_publisher import EventPublisher
from k9_dow.persistence.file_repository import FileRepository
from k9_dow.squads.src.base_stage_squad import BaseStageSquad


class Stage3DataRequirementsSquad(BaseStageSquad):

    squad_id = "stage3_data_requirements"
    stage_name = "Required Data Identification"
    stage_num = 3

    def build_agents(self) -> list[BaseDowAgent]:
        kwargs = {
            "config": self.config,
            "event_publisher": self.event_publisher,
        }
        return [
            DataRequirementsAgent(**kwargs),
            CapabilityExtractorAgent(**kwargs),
            DM2ExtractorAgent(**kwargs),
            SystemServiceExtractorAgent(**kwargs),
            SystemViewAgent(**kwargs),
            SummarizerAgent(**kwargs),
            GovernanceAgent(**kwargs),
        ]
