# SPDX-License-Identifier: Apache-2.0

import uuid
from datetime import datetime, timezone


def generate_job_id() -> str:
    ts = datetime.now(timezone.utc).strftime("%Y%m%d")
    short = uuid.uuid4().hex[:6].upper()
    return f"JOB-{ts}-{short}"


def generate_stage_id(stage_num: int, stage_name: str) -> str:
    safe = stage_name.replace(" ", "_").replace("/", "_")[:30]
    return f"stage{stage_num}_{safe}"
