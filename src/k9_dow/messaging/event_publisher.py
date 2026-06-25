# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any

from k9_dow.contracts.events import DowEvent

log = logging.getLogger(__name__)


class EventPublisher(ABC):
    @abstractmethod
    def publish(self, event: DowEvent) -> None:
        raise NotImplementedError


class InMemoryEventPublisher(EventPublisher):
    """Event publisher for tests and local development."""

    def __init__(self):
        self._events: list[DowEvent] = []

    def publish(self, event: DowEvent) -> None:
        self._events.append(event)
        log.info(
            "[Event] %s | job=%s stage=%s agent=%s | %s",
            event.event_type,
            event.job_id,
            event.stage_id,
            event.agent_name,
            event.message,
        )

    @property
    def events(self) -> list[DowEvent]:
        return list(self._events)

    def events_for_job(self, job_id: str) -> list[DowEvent]:
        return [e for e in self._events if e.job_id == job_id]

    def clear(self) -> None:
        self._events.clear()
