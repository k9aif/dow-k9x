from __future__ import annotations

import re
import logging
from pathlib import Path

log = logging.getLogger(__name__)

_TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "templates"
_NOT_PROVIDED = "NOT PROVIDED IN SOURCE"


class TemplateEngine:

    def __init__(self, template_name: str = "icd_template.md") -> None:
        self._template_path = _TEMPLATE_DIR / template_name

    def load(self) -> str:
        return self._template_path.read_text(encoding="utf-8")

    def resolve(self, tokens: dict[str, str]) -> str:
        template = self.load()
        def replacer(match):
            key = match.group(1).strip()
            value = tokens.get(key, "")
            if not value or not value.strip():
                return _NOT_PROVIDED
            return value
        return re.sub(r"\{\{\s*(\w+)\s*\}\}", replacer, template)
