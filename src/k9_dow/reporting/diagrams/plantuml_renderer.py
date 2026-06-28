from __future__ import annotations

import logging
import os
import subprocess
import tempfile
from pathlib import Path

log = logging.getLogger(__name__)


class PlantUmlRenderer:

    def __init__(self, binary: str | None = None) -> None:
        self._binary = binary or os.environ.get("PLANTUML_BIN", "plantuml")

    def render_png(self, puml: str) -> bytes | None:
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                puml_path = Path(tmpdir) / "diagram.puml"
                png_path = Path(tmpdir) / "diagram.png"
                puml_path.write_text(puml, encoding="utf-8")

                result = subprocess.run(
                    [self._binary, "-tpng", str(puml_path)],
                    capture_output=True, timeout=30,
                )
                if result.returncode != 0:
                    log.warning("[PlantUML] render failed: %s", result.stderr.decode()[:200])
                    return None

                if png_path.exists():
                    return png_path.read_bytes()

                log.warning("[PlantUML] PNG not found after render")
                return None

        except FileNotFoundError:
            log.warning("[PlantUML] Binary not found: %s — diagrams will be skipped", self._binary)
            return None
        except subprocess.TimeoutExpired:
            log.warning("[PlantUML] Render timed out")
            return None
