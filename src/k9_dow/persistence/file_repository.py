# SPDX-License-Identifier: Apache-2.0

import json
import logging
from pathlib import Path
from typing import Any, Optional

from k9_dow.utils.file_utils import ensure_dir

log = logging.getLogger(__name__)


class FileRepository:
    """File-based persistence for job artifacts.

    Directory layout:
        output_reports/{job_id}/
            input/           — raw uploaded files
            stage_outputs/   — per-stage markdown reports
            json/            — structured JSON artifacts
            reports/         — final report packages
            logs/            — event logs
    """

    def __init__(self, base_dir: str | Path = "output_reports"):
        self._base = Path(base_dir)

    def job_dir(self, job_id: str) -> Path:
        return ensure_dir(self._base / job_id)

    def input_dir(self, job_id: str) -> Path:
        return ensure_dir(self.job_dir(job_id) / "input")

    def stage_dir(self, job_id: str) -> Path:
        return ensure_dir(self.job_dir(job_id) / "stage_outputs")

    def json_dir(self, job_id: str) -> Path:
        return ensure_dir(self.job_dir(job_id) / "json")

    def reports_dir(self, job_id: str) -> Path:
        return ensure_dir(self.job_dir(job_id) / "reports")

    def logs_dir(self, job_id: str) -> Path:
        return ensure_dir(self.job_dir(job_id) / "logs")

    def save_input(self, job_id: str, filename: str, data: bytes) -> Path:
        path = self.input_dir(job_id) / filename
        path.write_bytes(data)
        log.info("[FileRepo] Saved input: %s", path)
        return path

    def save_markdown(self, job_id: str, filename: str, content: str) -> Path:
        path = self.stage_dir(job_id) / filename
        path.write_text(content, encoding="utf-8")
        log.info("[FileRepo] Saved markdown: %s", path)
        return path

    def save_json(self, job_id: str, filename: str, data: Any) -> Path:
        path = self.json_dir(job_id) / filename
        path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
        log.info("[FileRepo] Saved JSON: %s", path)
        return path

    def save_report(self, job_id: str, filename: str, content: str) -> Path:
        path = self.reports_dir(job_id) / filename
        path.write_text(content, encoding="utf-8")
        log.info("[FileRepo] Saved report: %s", path)
        return path

    def save_event_log(self, job_id: str, events: list[dict]) -> Path:
        path = self.logs_dir(job_id) / "events.json"
        path.write_text(json.dumps(events, indent=2, default=str), encoding="utf-8")
        return path

    def load_markdown(self, job_id: str, filename: str) -> Optional[str]:
        path = self.stage_dir(job_id) / filename
        if not path.exists():
            return None
        return path.read_text(encoding="utf-8")

    def load_json(self, job_id: str, filename: str) -> Optional[dict]:
        path = self.json_dir(job_id) / filename
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))

    def list_artifacts(self, job_id: str) -> dict[str, list[str]]:
        result: dict[str, list[str]] = {}
        job = self.job_dir(job_id)
        for subdir in ["input", "stage_outputs", "json", "reports", "logs"]:
            d = job / subdir
            if d.exists():
                result[subdir] = sorted(f.name for f in d.iterdir() if f.is_file())
        return result

    def build_artifact_index(self, job_id: str) -> dict:
        index = {"job_id": job_id, "artifacts": {}}
        job = self.job_dir(job_id)
        for subdir in ["input", "stage_outputs", "json", "reports"]:
            d = job / subdir
            if d.exists():
                for f in sorted(d.iterdir()):
                    if f.is_file():
                        index["artifacts"][f.name] = str(f.relative_to(self._base))
        return index

    def save_artifact_index(self, job_id: str) -> Path:
        index = self.build_artifact_index(job_id)
        return self.save_json(job_id, "artifact_index.json", index)
