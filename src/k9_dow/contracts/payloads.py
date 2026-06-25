# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


class DocumentInput(BaseModel):
    job_id: str
    filename: str
    content_type: str
    raw_path: Optional[str] = None
    text: Optional[str] = None
    markdown: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class RoutingDecision(BaseModel):
    job_id: str
    classification: Literal["BD", "DODAF", "JCIDS", "SE", "UNKNOWN"]
    document_type: str
    route_to: str
    dodaf_eligible: bool = False
    jcids_eligible: bool = False
    se_eligible: bool = False
    recommended_stages: list[str | int] = Field(default_factory=list)
    confidence: float = 1.0
    rationale: str = ""
    matched_rules: list[str] = Field(default_factory=list)


class DowAgentPayload(BaseModel):
    job_id: str
    stage_id: str
    agent_name: str
    source_markdown: str
    prior_outputs: dict[str, str] = Field(default_factory=dict)
    routing_decision: Optional[RoutingDecision] = None
    document_type: Optional[str] = None
    mission_context: Optional[str] = None
    viewpoint: Optional[str] = None
    entities: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class StageExecutionContext(BaseModel):
    job_id: str
    route: str
    stage_id: str
    stage_name: str
    source_document: str
    normalized_markdown: str
    prior_stage_outputs: dict[str, str] = Field(default_factory=dict)
    routing_decision: Optional[RoutingDecision] = None
    metadata: dict[str, Any] = Field(default_factory=dict)
