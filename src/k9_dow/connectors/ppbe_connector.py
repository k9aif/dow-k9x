from __future__ import annotations

from typing import Any

from k9_dow.connectors.base_connector import BaseConnector


class PPBEConnector(BaseConnector):
    """PPBE / Financial system — funding lines.

    Mode: Read only.
    This is a stub — replace with actual financial system API.
    """

    def __init__(self, base_url: str = "", api_key: str = "") -> None:
        self._base_url = base_url
        self._api_key = api_key

    def read(self, query: dict[str, Any]) -> list[dict]:
        return [
            {
                "id": "FL-FY26-001",
                "program_element": "PE-0604015F",
                "description": "Stub funding line",
                "fiscal_year": "FY2026",
                "amount": 0.0,
                "status": "current",
                "source": "PPBE_STUB",
            }
        ]

    def get_funding_lines(self, program_element: str) -> list[dict]:
        return self.read({"pe": program_element})
