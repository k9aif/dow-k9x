# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

from pydantic import BaseModel, Field


class DowEvent(BaseModel):
    event_type: str
    job_id: str
    route: str = ""
    stage_id: str = ""
    agent_name: str = ""
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: str = ""
    message: str = ""
    payload: dict[str, Any] = Field(default_factory=dict)
