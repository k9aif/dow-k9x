from __future__ import annotations

from typing import Any

from k9_dow.connectors.base_connector import BaseConnector


class CameoConnector(BaseConnector):
    """Cameo / MagicDraw (SysML/MBSE) — architecture + DoDAF model.

    Mode: Read only; generate views from model.
    This is a stub — replace with actual Cameo Teamwork Cloud API.
    """

    def __init__(self, base_url: str = "", api_key: str = "") -> None:
        self._base_url = base_url
        self._api_key = api_key

    def read(self, query: dict[str, Any]) -> list[dict]:
        view_type = query.get("view_type", "OV-1")
        return [
            {
                "id": f"VIEW-{view_type}-001",
                "view_type": view_type,
                "title": f"Stub {view_type} View",
                "elements": [],
                "source": "CAMEO_STUB",
            }
        ]

    def get_dodaf_views(self, view_family: str = "OV") -> list[dict]:
        return self.read({"view_type": f"{view_family}-1"})

    def get_model_elements(self, block_id: str) -> list[dict]:
        return [{"id": block_id, "type": "Block", "name": "StubBlock", "source": "CAMEO_STUB"}]
