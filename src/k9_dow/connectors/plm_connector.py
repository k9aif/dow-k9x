from __future__ import annotations

from typing import Any

from k9_dow.connectors.base_connector import BaseConnector


class PLMConnector(BaseConnector):
    """PLM — technical baseline, configuration management.

    Mode: Read only.
    This is a stub — replace with actual PLM system API.
    """

    def __init__(self, base_url: str = "", api_key: str = "") -> None:
        self._base_url = base_url
        self._api_key = api_key

    def read(self, query: dict[str, Any]) -> list[dict]:
        return [
            {
                "id": "TBI-001",
                "name": "Crypto Module v2.1",
                "subsystem": "Communications",
                "baseline_rev": "BL-3.0",
                "status": "current",
                "source": "PLM_STUB",
            }
        ]

    def get_baseline_items(self, baseline_rev: str) -> list[dict]:
        return self.read({"baseline": baseline_rev})
