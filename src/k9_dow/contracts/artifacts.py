# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


class DowAgentResult(BaseModel):
    job_id: str
    agent_name: str
    stage_id: str
    status: Literal["completed", "failed", "skipped"] = "completed"
    markdown: str = ""
    json_data: dict[str, Any] = Field(default_factory=dict)
    citations: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)


class GovernanceFinding(BaseModel):
    severity: Literal["info", "warning", "error", "blocker"]
    rule_id: str
    message: str
    evidence: Optional[str] = None
    recommended_action: Optional[str] = None


class GovernanceResult(BaseModel):
    status: Literal["pass", "warn", "block"] = "pass"
    findings: list[GovernanceFinding] = Field(default_factory=list)
    summary: str = ""
