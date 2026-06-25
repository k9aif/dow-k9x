# SPDX-License-Identifier: Apache-2.0

"""Stage 6 — Presentation and Reporting Squad."""

from __future__ import annotations

from typing import Any, Dict, Optional

from k9_dow.agents.src.base_dow_agent import BaseDowAgent
from k9_dow.agents.src.verification_agent import VerificationAgent
from k9_dow.agents.src.presentation_agent import PresentationAgent
from k9_dow.agents.src.summarizer_agent import SummarizerAgent
from k9_dow.agents.src.governance_agent import GovernanceAgent
from k9_dow.agents.src.report_writer_agent import ReportWriterAgent
from k9_dow.messaging.event_publisher import EventPublisher
from k9_dow.persistence.file_repository import FileRepository
from k9_dow.squads.src.base_stage_squad import BaseStageSquad


class Stage6PresentationSquad(BaseStageSquad):

    squad_id = "stage6_presentation"
    stage_name = "Presentation and Reporting"
    stage_num = 6

    def build_agents(self) -> list[BaseDowAgent]:
        kwargs = {
            "config": self.config,
            "event_publisher": self.event_publisher,
        }
        return [
            VerificationAgent(**kwargs),
            PresentationAgent(**kwargs),
            SummarizerAgent(**kwargs),
            GovernanceAgent(**kwargs),
            ReportWriterAgent(**kwargs),
        ]
