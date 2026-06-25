# SPDX-License-Identifier: Apache-2.0

"""Stage 4 — Architecture Data Correlation Squad."""

from __future__ import annotations

from typing import Any, Dict, Optional

from k9_dow.agents.src.base_dow_agent import BaseDowAgent
from k9_dow.agents.src.operational_extractor_agent import OperationalExtractorAgent
from k9_dow.agents.src.capability_extractor_agent import CapabilityExtractorAgent
from k9_dow.agents.src.system_service_extractor_agent import SystemServiceExtractorAgent
from k9_dow.agents.src.system_view_agent import SystemViewAgent
from k9_dow.agents.src.services_view_agent import ServicesViewAgent
from k9_dow.agents.src.dm2_extractor_agent import DM2ExtractorAgent
from k9_dow.agents.src.data_correlation_agent import DataCorrelationAgent
from k9_dow.agents.src.report_writer_agent import ReportWriterAgent
from k9_dow.agents.src.summarizer_agent import SummarizerAgent
from k9_dow.agents.src.governance_agent import GovernanceAgent
from k9_dow.messaging.event_publisher import EventPublisher
from k9_dow.persistence.file_repository import FileRepository
from k9_dow.squads.src.base_stage_squad import BaseStageSquad


class Stage4ArchitectureCorrelationSquad(BaseStageSquad):

    squad_id = "stage4_architecture_correlation"
    stage_name = "Architecture Data Correlation"
    stage_num = 4

    def build_agents(self) -> list[BaseDowAgent]:
        kwargs = {
            "config": self.config,
            "event_publisher": self.event_publisher,
        }
        return [
            OperationalExtractorAgent(**kwargs),
            CapabilityExtractorAgent(**kwargs),
            SystemServiceExtractorAgent(**kwargs),
            SystemViewAgent(**kwargs),
            ServicesViewAgent(**kwargs),
            DM2ExtractorAgent(**kwargs),
            DataCorrelationAgent(**kwargs),
            ReportWriterAgent(**kwargs),
            SummarizerAgent(**kwargs),
            GovernanceAgent(**kwargs),
        ]
