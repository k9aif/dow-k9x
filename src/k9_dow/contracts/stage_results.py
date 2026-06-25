# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field

from k9_dow.contracts.artifacts import DowAgentResult, GovernanceResult


class StageResult(BaseModel):
    job_id: str
    stage_id: str
    stage_name: str
    status: Literal["completed", "failed", "blocked", "needs_human_review"] = "completed"
    agent_results: list[DowAgentResult] = Field(default_factory=list)
    markdown_report: str = ""
    json_bundle: dict[str, Any] = Field(default_factory=dict)
    governance: GovernanceResult = Field(default_factory=GovernanceResult)
    artifact_paths: list[str] = Field(default_factory=list)
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None

    def mark_complete(self) -> None:
        self.completed_at = datetime.now(timezone.utc)
        if self.status == "completed":
            return
        has_failures = any(r.status == "failed" for r in self.agent_results)
        has_blockers = self.governance.status == "block"
        if has_blockers:
            self.status = "blocked"
        elif has_failures:
            self.status = "failed"
        else:
            self.status = "completed"


class JobResult(BaseModel):
    job_id: str
    route: str
    classification: str
    status: Literal["completed", "failed", "blocked", "needs_human_review", "running"] = "running"
    stage_results: list[StageResult] = Field(default_factory=list)
    artifact_index: dict[str, str] = Field(default_factory=dict)
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
