from __future__ import annotations

from typing import Any

from k9_dow.connectors.base_connector import BaseConnector


class DoorsConnector(BaseConnector):
    """DOORS / DOORS Next — requirements of record.

    Mode: Read + write-back (proposed links staged for human).
    This is a stub — replace with actual DOORS Next REST API integration.
    """

    def __init__(self, base_url: str = "", api_key: str = "") -> None:
        self._base_url = base_url
        self._api_key = api_key

    def read(self, query: dict[str, Any]) -> list[dict]:
        return [
            {
                "id": "REQ-001",
                "shall_text": "The system shall provide encrypted communications.",
                "type": "functional",
                "module": query.get("module", "default"),
                "status": "approved",
                "source": "DOORS_STUB",
            }
        ]

    def get_requirements_by_module(self, module_id: str) -> list[dict]:
        return self.read({"module": module_id})

    def get_trace_links(self, req_id: str) -> list[dict]:
        return [{"from": req_id, "to": "REQ-002", "link_type": "derives", "source": "DOORS_STUB"}]
