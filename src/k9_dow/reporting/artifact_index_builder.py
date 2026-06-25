# SPDX-License-Identifier: Apache-2.0

"""Artifact index builder — creates artifact_index.json for a job."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from k9_dow.contracts.stage_results import JobResult


class ArtifactIndexBuilder:
    """Builds a structured artifact index from job results."""

    def build(self, job_result: JobResult) -> dict[str, Any]:
        index: dict[str, Any] = {
            "job_id": job_result.job_id,
            "classification": job_result.classification,
            "route": job_result.route,
            "status": job_result.status,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "stages": [],
            "artifacts": {},
        }

        for stage in job_result.stage_results:
            stage_entry = {
                "stage_id": stage.stage_id,
                "stage_name": stage.stage_name,
                "status": stage.status,
                "governance": stage.governance.status,
                "artifact_count": len(stage.artifact_paths),
                "artifacts": stage.artifact_paths,
            }
            index["stages"].append(stage_entry)

            for path in stage.artifact_paths:
                name = path.rsplit("/", 1)[-1] if "/" in path else path
                index["artifacts"][name] = path

        return index
