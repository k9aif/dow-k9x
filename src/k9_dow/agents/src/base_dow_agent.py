# SPDX-License-Identifier: Apache-2.0

"""
BaseDowAgent — domain base class for all DoW agents.

Extends K9-AIF BaseAgent with typed payloads, event publication,
governance grounding rules, and LLM invocation via llm_invoke.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from k9_aif_abb.k9_core.agent.base_agent import BaseAgent
from k9_aif_abb.k9_inference.models.inference_request import InferenceRequest
from k9_aif_abb.k9_utils.llm_invoke import llm_invoke

from k9_dow.contracts.artifacts import DowAgentResult
from k9_dow.contracts.payloads import DowAgentPayload
from k9_dow.contracts.events import DowEvent
from k9_dow.config.settings import settings


class BaseDowAgent(BaseAgent):
    """
    Domain base class for all DoW workbench agents.

    Subclasses implement run_agent() with typed payload/result.
    BaseDowAgent handles event publication, grounding rules injection,
    error wrapping, and LLM invocation.
    """

    layer: str = "DoW Agent"
    agent_name: str = "BaseDowAgent"

    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        monitor=None,
        message_bus=None,
        governance=None,
        event_publisher=None,
    ):
        super().__init__(
            config=config,
            monitor=monitor,
            message_bus=message_bus,
            governance=governance,
        )
        self._event_publisher = event_publisher
        self._grounding_rules = settings.common_grounding_rules()
        self._governance_rules = settings.governance_rules()

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        agent_payload = DowAgentPayload(**payload) if isinstance(payload, dict) else payload
        self._emit_event(agent_payload.job_id, agent_payload.stage_id, "AgentStarted")

        try:
            result = self.run_agent(agent_payload)
            self._emit_event(
                result.job_id, result.stage_id, "AgentCompleted",
                status=result.status,
            )
            return result.model_dump()
        except Exception as exc:
            self.logger.error("[%s] %s failed: %s", self.layer, self.agent_name, exc)
            self._emit_event(
                agent_payload.job_id, agent_payload.stage_id, "AgentFailed",
                status="failed", message=str(exc),
            )
            return DowAgentResult(
                job_id=agent_payload.job_id,
                agent_name=self.agent_name,
                stage_id=agent_payload.stage_id,
                status="failed",
                errors=[str(exc)],
            ).model_dump()

    def run_agent(self, payload: DowAgentPayload) -> DowAgentResult:
        """Override in subclasses — domain-specific agent logic."""
        raise NotImplementedError(f"{self.agent_name} must implement run_agent()")

    # ── LLM helpers ───────────────────────────────────────────────────────

    def invoke_llm(
        self,
        prompt: str,
        task_type: str = "reasoning",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        full_prompt = f"{self._grounding_rules}\n\n{prompt}"
        req = InferenceRequest(
            prompt=full_prompt,
            task_type=task_type,
            metadata=metadata or {"agent": self.agent_name},
        )
        resp = llm_invoke(self.config, req)
        return (resp.output or "").strip()

    def build_prompt(self, role: str, task: str, source_text: str, prior_outputs: str = "") -> str:
        parts = [
            f"Role: {role}",
            f"Task: {task}",
        ]
        if prior_outputs:
            parts.append(f"\n## Prior Stage Outputs\n{prior_outputs}")
        parts.append(f"\n## Source Document\n{source_text[:8000]}")
        return "\n\n".join(parts)

    # ── Event helpers ─────────────────────────────────────────────────────

    def _emit_event(
        self,
        job_id: str,
        stage_id: str,
        event_type: str,
        status: str = "",
        message: str = "",
    ) -> None:
        event = DowEvent(
            event_type=event_type,
            job_id=job_id,
            stage_id=stage_id,
            agent_name=self.agent_name,
            status=status,
            message=message or f"{self.agent_name} {event_type}",
        )
        if self._event_publisher:
            self._event_publisher.publish(event)
        self.publish_event(event.model_dump())
