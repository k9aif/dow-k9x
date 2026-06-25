# SPDX-License-Identifier: Apache-2.0

from pathlib import Path


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def safe_filename(name: str) -> str:
    return name.replace(" ", "_").replace("/", "_").replace("\\", "_")
