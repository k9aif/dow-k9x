from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseConnector(ABC):
    """Base contract for authoritative source connectors.

    From spec Section 7: never treat a scraped document as source of truth.
    Agents read authoritative records; all write-backs are staged as
    proposals pending HITL approval.
    """

    @abstractmethod
    def read(self, query: dict[str, Any]) -> list[dict]:
        ...

    def propose_write(self, entity_id: str, changes: dict[str, Any]) -> dict:
        """Stage a proposed change for HITL approval. Never writes directly."""
        return {
            "connector": self.__class__.__name__,
            "entity_id": entity_id,
            "proposed_changes": changes,
            "status": "staged_for_human_review",
        }
