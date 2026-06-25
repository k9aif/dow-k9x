# SPDX-License-Identifier: Apache-2.0
# DoW Architecture Workbench — DodafOrchestrator (SBB)
#
# Executes the 6-stage DoDAF 2.0 pipeline sequentially.
# Uses AgentRegistry + SquadLoader from K9-AIF framework — no custom squad classes.
#
# Pattern: same as EOC ClaimsProcessingOrchestrator.

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, Optional

from k9_aif_abb.k9_agents.registry.agent_registry import AgentRegistry
from k9_aif_abb.k9_core.orchestration.base_orchestrator import BaseOrchestrator
from k9_aif_abb.k9_squad.squad_loader import SquadLoader

from k9_dow.utils.agent_loader import AgentLoader
from k9_dow.config.settings import settings

# Stage agent imports
from k9_dow.agents.src.validation_agent import ValidationAgent
from k9_dow.agents.src.stakeholder_extractor_agent import StakeholderExtractorAgent
from k9_dow.agents.src.pain_point_extractor_agent import PainPointExtractorAgent
from k9_dow.agents.src.objective_extractor_agent import ObjectiveExtractorAgent
from k9_dow.agents.src.mission_assessment_agent import MissionAssessmentAgent
from k9_dow.agents.src.f2p_intent_agent import F2PIntentAgent
from k9_dow.agents.src.summarizer_agent import SummarizerAgent
from k9_dow.agents.src.governance_agent import GovernanceAgent
from k9_dow.agents.src.project_scope_agent import ProjectScopeAgent
from k9_dow.agents.src.constraint_agent import ConstraintAgent
from k9_dow.agents.src.operational_extractor_agent import OperationalExtractorAgent
from k9_dow.agents.src.capability_extractor_agent import CapabilityExtractorAgent
from k9_dow.agents.src.risk_extractor_agent import RiskExtractorAgent
from k9_dow.agents.src.vocabulary_agent import VocabularyAgent
from k9_dow.agents.src.architecture_analyzer_agent import ArchitectureAnalyzerAgent
from k9_dow.agents.src.requirement_agent import RequirementAgent
from k9_dow.agents.src.data_requirements_agent import DataRequirementsAgent
from k9_dow.agents.src.dm2_extractor_agent import DM2ExtractorAgent
from k9_dow.agents.src.system_service_extractor_agent import SystemServiceExtractorAgent
from k9_dow.agents.src.system_view_agent import SystemViewAgent
from k9_dow.agents.src.services_view_agent import ServicesViewAgent
from k9_dow.agents.src.data_correlation_agent import DataCorrelationAgent
from k9_dow.agents.src.capability_analyzer_agent import CapabilityAnalyzerAgent
from k9_dow.agents.src.operational_analyzer_agent import OperationalAnalyzerAgent
from k9_dow.agents.src.verification_agent import VerificationAgent
from k9_dow.agents.src.action_item_agent import ActionItemAgent
from k9_dow.agents.src.presentation_agent import PresentationAgent
from k9_dow.agents.src.report_writer_agent import ReportWriterAgent

log = logging.getLogger(__name__)

# All agents registered for SquadLoader — maps class name to class
_ALL_AGENTS = {
    "ValidationAgent": ValidationAgent,
    "StakeholderExtractorAgent": StakeholderExtractorAgent,
    "PainPointExtractorAgent": PainPointExtractorAgent,
    "ObjectiveExtractorAgent": ObjectiveExtractorAgent,
    "MissionAssessmentAgent": MissionAssessmentAgent,
    "F2PIntentAgent": F2PIntentAgent,
    "SummarizerAgent": SummarizerAgent,
    "GovernanceAgent": GovernanceAgent,
    "ProjectScopeAgent": ProjectScopeAgent,
    "ConstraintAgent": ConstraintAgent,
    "OperationalExtractorAgent": OperationalExtractorAgent,
    "CapabilityExtractorAgent": CapabilityExtractorAgent,
    "RiskExtractorAgent": RiskExtractorAgent,
    "VocabularyAgent": VocabularyAgent,
    "ArchitectureAnalyzerAgent": ArchitectureAnalyzerAgent,
    "RequirementAgent": RequirementAgent,
    "DataRequirementsAgent": DataRequirementsAgent,
    "DM2ExtractorAgent": DM2ExtractorAgent,
    "SystemServiceExtractorAgent": SystemServiceExtractorAgent,
    "SystemViewAgent": SystemViewAgent,
    "ServicesViewAgent": ServicesViewAgent,
    "DataCorrelationAgent": DataCorrelationAgent,
    "CapabilityAnalyzerAgent": CapabilityAnalyzerAgent,
    "OperationalAnalyzerAgent": OperationalAnalyzerAgent,
    "VerificationAgent": VerificationAgent,
    "ActionItemAgent": ActionItemAgent,
    "PresentationAgent": PresentationAgent,
    "ReportWriterAgent": ReportWriterAgent,
}

# Stage sequence — squad_id must match the key in squads/yaml/*.yaml
_STAGE_SEQUENCE = [
    (1, "Stage1FitForPurposeSquad", "stage1_fit_for_purpose_squad.yaml"),
    (2, "Stage2ScopeIcdSquad", "stage2_scope_icd_squad.yaml"),
    (3, "Stage3DataRequirementsSquad", "stage3_data_requirements_squad.yaml"),
    (4, "Stage4ArchitectureCorrelationSquad", "stage4_architecture_correlation_squad.yaml"),
    (5, "Stage5ArchitectureAnalysisSquad", "stage5_architecture_analysis_squad.yaml"),
    (6, "Stage6PresentationSquad", "stage6_presentation_squad.yaml"),
]


class DodafOrchestrator(BaseOrchestrator):
    """
    DoDAF Pipeline Orchestrator (SBB).

    Extends BaseOrchestrator. Executes Stages 1-6 sequentially.
    Each stage is a BaseSquad loaded from YAML via SquadLoader.
    """

    layer = "DoDAF Orchestrator SBB"

    def __init__(self, config: Optional[Dict[str, Any]] = None, **kwargs) -> None:
        super().__init__(config=config or {}, **kwargs)
        self._squads_yaml_dir = self._resolve_squads_dir()
        self._agents_yaml_dir = self._resolve_agents_dir()

    def _resolve_squads_dir(self) -> Path:
        here = Path(__file__).resolve().parent.parent
        return here / "squads" / "yaml"

    def _resolve_agents_dir(self) -> Path:
        here = Path(__file__).resolve().parent.parent
        return here / "agents" / "yaml"

    def _load_squad(self, squad_yaml_filename: str, squad_id: str):
        agent_loader = AgentLoader(self._agents_yaml_dir)
        agent_registry = AgentRegistry()

        for name, cls in _ALL_AGENTS.items():
            agent_registry.register(
                name,
                lambda c=cls, n=name: c(
                    config=agent_loader.merge_with_global(n, self.config)
                ),
            )

        loader = SquadLoader(agent_registry)
        squad_path = self._squads_yaml_dir / squad_yaml_filename
        squad = loader.load_one(str(squad_path), squad_id)

        log.info(
            "[DodafOrchestrator] Squad loaded: %s — %d agents, %d flow steps",
            squad_id, len(squad.agents), len(squad.flow),
        )
        return squad

    def execute_flow(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        job_id = payload.get("job_id", "unknown")
        normalized_md = payload.get("normalized_markdown", "")

        log.info("[DodafOrchestrator] Starting DoDAF pipeline for job=%s", job_id)

        accumulated_outputs: Dict[str, str] = {}
        stage_results = []

        for stage_num, squad_id, yaml_file in _STAGE_SEQUENCE:
            log.info(
                "[DodafOrchestrator] Stage %d — loading %s", stage_num, squad_id,
            )

            try:
                squad = self._load_squad(yaml_file, squad_id)
            except Exception as exc:
                log.error("[DodafOrchestrator] Failed to load squad %s: %s", squad_id, exc)
                stage_results.append({
                    "stage": stage_num, "squad_id": squad_id,
                    "status": "failed", "error": str(exc),
                })
                continue

            stage_payload = {
                **payload,
                "source_markdown": normalized_md,
                "normalized_markdown": normalized_md,
                "prior_outputs": accumulated_outputs,
                "stage_num": stage_num,
            }

            try:
                result = squad.execute(stage_payload)
                stage_results.append({
                    "stage": stage_num, "squad_id": squad_id,
                    "status": "completed", "result": result,
                })

                for key, value in result.items():
                    if isinstance(value, str) and len(value) > 50:
                        accumulated_outputs[f"stage{stage_num}_{key}"] = value

            except Exception as exc:
                log.error(
                    "[DodafOrchestrator] Stage %d failed: %s", stage_num, exc,
                )
                stage_results.append({
                    "stage": stage_num, "squad_id": squad_id,
                    "status": "failed", "error": str(exc),
                })
                break

            if stage_num == 2 and settings.REQUIRE_HIL_AFTER_STAGE2:
                log.info("[DodafOrchestrator] HIL gate after Stage 2 — pausing")
                return {
                    "job_id": job_id, "status": "needs_human_review",
                    "stage_results": stage_results,
                    "accumulated_outputs": accumulated_outputs,
                }

        log.info(
            "[DodafOrchestrator] DoDAF pipeline completed for job=%s (%d stages)",
            job_id, len(stage_results),
        )

        return {
            "job_id": job_id,
            "status": "completed",
            "pipeline": "dodaf",
            "stage_results": stage_results,
            "accumulated_outputs": accumulated_outputs,
        }
