# SPDX-License-Identifier: Apache-2.0
# K9-AIF Framework
"""DAS_INSTANCE: run a second DAS (e.g. das-next) beside the live one on the same Kafka,
MinIO and job queue without either taking the other's work.

Unset (the default), every name is exactly what it always was. Set (``next``), the
names this instance owns get its own variant:

- internal Kafka topics: ``next.dow.router.in``, ``next.das.results``, ``next.das.msa`` ...
- consumer groups and the job queue: ``dow-router-next``, ``das-job-queue-next`` ...
- object storage keys: ``next/by-job/<job>/...`` in the same bucket

K9X HIL task and reply topics are not renamed: HIL is shared, and each gate has its own
queue, so a decision reaches the instance that raised the task.
"""

from __future__ import annotations

import os


def instance() -> str:
    return os.environ.get("DAS_INSTANCE", "").strip().lower()


def topic(name: str) -> str:
    inst = instance()
    return f"{inst}.{name}" if inst else name


def group(name: str) -> str:
    inst = instance()
    return f"{name}-{inst}" if inst else name


def key_prefix() -> str:
    inst = instance()
    return f"{inst}/" if inst else ""
