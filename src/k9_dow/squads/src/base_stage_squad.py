# SPDX-License-Identifier: Apache-2.0

"""
BaseStageSquad — domain base class for all DoW stage squads.

Sequences agents, accumulates results into a StageResult,
runs governance review, persists outputs, and publishes events.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from k9_dow.agents.src.base_dow_agent import BaseDowAgent
from k9_dow.contracts.artifacts import DowAgentResult, GovernanceResult
from k9_dow.contracts.events import DowEvent
from k9_dow.contracts.payloads import DowAgentPayload, StageExecutionContext
from k9_dow.contracts.stage_results import StageResult
from k9_dow.messaging.event_publisher import EventPublisher
from k9_dow.persistence.file_repository import FileRepository

log = logging.getLogger(__name__)


class BaseStageSquad:
    """
    Executes a sequence of BaseDowAgent instances for a single stage.

    Subclasses define the agent list and stage metadata by overriding
    squad_id, stage_name, stage_num, and build_agents().
    """

    squad_id: str = "base_stage_squad"
    stage_name: str = "Base Stage"
    stage_num: int = 0

    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        event_publisher: Optional[EventPublisher] = None,
        file_repo: Optional[FileRepository] = None,
    ):
        self.config = config or {}
        self.event_publisher = event_publisher
        self.file_repo = file_repo or FileRepository()
        self.logger = logging.getLogger(self.__class__.__name__)

    def build_agents(self) -> list[BaseDowAgent]:
        """Override — return ordered list of agents for this stage."""
        raise NotImplementedError(f"{self.squad_id} must implement build_agents()")

    def execute(self, context: StageExecutionContext) -> StageResult:
        result = StageResult(
            job_id=context.job_id,
            stage_id=context.stage_id,
            stage_name=self.stage_name,
        )

        self._emit("StageStarted", context.job_id, context.stage_id)
        self.logger.info(
            "[%s] Stage %d — %s started | job=%s",
            self.squad_id, self.stage_num, self.stage_name, context.job_id,
        )

        agents = self.build_agents()
        accumulated_outputs: dict[str, str] = dict(context.prior_stage_outputs)

        for agent in agents:
            agent_payload = DowAgentPayload(
                job_id=context.job_id,
                stage_id=context.stage_id,
                agent_name=agent.agent_name,
                source_markdown=context.normalized_markdown,
                prior_outputs=accumulated_outputs,
                routing_decision=context.routing_decision,
                metadata=context.metadata,
            )

            try:
                raw_result = agent.execute(agent_payload.model_dump())
                agent_result = DowAgentResult(**raw_result)
            except Exception as exc:
                self.logger.error(
                    "[%s] Agent %s failed: %s", self.squad_id, agent.agent_name, exc,
                )
                agent_result = DowAgentResult(
                    job_id=context.job_id,
                    agent_name=agent.agent_name,
                    stage_id=context.stage_id,
                    status="failed",
                    errors=[str(exc)],
                )

            result.agent_results.append(agent_result)

            if agent_result.status == "completed" and agent_result.markdown:
                accumulated_outputs[agent.agent_name] = agent_result.markdown

        result.markdown_report = self._assemble_report(result)
        result.governance = self._run_governance(result)
        result.mark_complete()

        self._persist(context.job_id, result)
        self._emit(
            "StageCompleted" if result.status == "completed" else "StageFailed",
            context.job_id, context.stage_id,
            status=result.status,
        )

        self.logger.info(
            "[%s] Stage %d — %s %s | job=%s",
            self.squad_id, self.stage_num, self.stage_name,
            result.status, context.job_id,
        )
        return result

    # ── Report assembly ───────────────────────────────────────────────────

    def _assemble_report(self, result: StageResult) -> str:
        sections = [f"# {self.stage_name}\n"]
        sections.append(f"**Job:** {result.job_id}  ")
        sections.append(f"**Stage:** {result.stage_id}\n")

        for ar in result.agent_results:
            if ar.markdown:
                sections.append(f"## {ar.agent_name}\n")
                sections.append(ar.markdown)
                sections.append("")
            if ar.warnings:
                sections.append(f"### Warnings ({ar.agent_name})")
                for w in ar.warnings:
                    sections.append(f"- {w}")
                sections.append("")

        return "\n".join(sections)

    # ── Governance ────────────────────────────────────────────────────────

    def _run_governance(self, result: StageResult) -> GovernanceResult:
        """Run governance checks on accumulated agent results.

        Subclasses can override to add a GovernanceAgent call.
        Default: pass if no agent failures, warn if any failures.
        """
        has_failures = any(r.status == "failed" for r in result.agent_results)
        if has_failures:
            return GovernanceResult(
                status="warn",
                summary="One or more agents failed during this stage.",
            )
        return GovernanceResult(status="pass", summary="All agents completed successfully.")

    # ── Persistence ───────────────────────────────────────────────────────

    def _persist(self, job_id: str, result: StageResult) -> None:
        if not self.file_repo:
            return
        try:
            artifact_name = f"stage{self.stage_num}_{self.stage_name.lower().replace(' ', '_').replace('/', '_')}.md"
            path = self.file_repo.save_markdown(job_id, artifact_name, result.markdown_report)
            result.artifact_paths.append(str(path))

            for ar in result.agent_results:
                if ar.json_data:
                    json_name = f"{ar.agent_name.lower()}.json"
                    jp = self.file_repo.save_json(job_id, json_name, ar.json_data)
                    result.artifact_paths.append(str(jp))
        except Exception as exc:
            self.logger.warning("[%s] Persistence failed: %s", self.squad_id, exc)

    # ── Events ────────────────────────────────────────────────────────────

    def _emit(
        self, event_type: str, job_id: str, stage_id: str = "",
        status: str = "", message: str = "",
    ) -> None:
        if not self.event_publisher:
            return
        self.event_publisher.publish(DowEvent(
            event_type=event_type,
            job_id=job_id,
            stage_id=stage_id or f"stage{self.stage_num}",
            status=status,
            message=message or f"{self.stage_name} {event_type}",
        ))
