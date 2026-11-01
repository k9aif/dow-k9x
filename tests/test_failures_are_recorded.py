# SPDX-License-Identifier: Apache-2.0
# K9-AIF Framework
"""v1.3.4: a failure on the way to a human decision is recorded, never carried on as success.

Before v1.3.4: a stage whose result could not be stored, or whose HIL task could not be
published, still reported success; a storage outage read as "no package", so an approval was
ignored; a failed read of the day's governance-alert log replaced the log with one alert; and a
drift check ran as a requirement run. Each test fails on v1.3.3.
"""

import json
import os

import pytest

os.environ.setdefault("K9_ENV", "test")

from k9_dow.gates import hil_gateway  # noqa: E402
from k9_dow.gates.hil_gateway import GateTaskPublishError, StageStoreError  # noqa: E402


class _Store:
    """Object storage as k9-aif 1.23 defines it: a missing object is FileNotFoundError; an
    unreachable store raises something else."""

    def __init__(self, objects=None, down=False):
        self.objects, self.down = dict(objects or {}), down

    def _check(self):
        if self.down:
            raise ConnectionError("object storage unreachable")

    def upload(self, bucket, key, data):
        self._check()
        self.objects[(bucket, key)] = data

    def download(self, bucket, key):
        self._check()
        if (bucket, key) not in self.objects:
            raise FileNotFoundError(key)
        return self.objects[(bucket, key)]

    def exists(self, bucket, key):
        from k9_aif_abb.k9_core.storage.base_object_storage import BaseObjectStorage
        return BaseObjectStorage.exists(self, bucket, key)

    def get_uri(self, bucket, key):
        return f"s3://{bucket}/{key}"


@pytest.fixture
def store(monkeypatch):
    holder = {"store": _Store()}
    from k9_aif_abb.k9_factories import object_storage_factory
    monkeypatch.setattr(object_storage_factory.ObjectStorageFactory, "create",
                        staticmethod(lambda config=None: holder["store"]))
    return holder


def test_a_stage_result_that_cannot_be_stored_raises(store):
    store["store"].down = True
    with pytest.raises(StageStoreError, match="was not stored"):
        hil_gateway.save_stage_result({}, "JOB-1", "requirement", {"status": "completed"})


def test_a_storage_outage_is_not_read_as_no_package(store):
    assert hil_gateway.stage_result_exists({}, "JOB-1", "requirement") is False      # truly absent
    store["store"].down = True
    with pytest.raises(ConnectionError):
        hil_gateway.stage_result_exists({}, "JOB-1", "requirement")


def test_loading_a_missing_result_is_none_but_an_outage_raises(store):
    assert hil_gateway.load_stage_result({}, "JOB-1", "requirement") is None
    store["store"].down = True
    with pytest.raises(StageStoreError, match="could not be read"):
        hil_gateway.load_stage_result({}, "JOB-1", "requirement")


def test_a_gate_task_that_cannot_be_published_raises(monkeypatch):
    from k9_aif_abb.k9_core.messaging import k9_event_bus

    class DownBus:
        def __init__(self, *a, **k):
            raise ConnectionError("broker unreachable")

    monkeypatch.setattr(k9_event_bus, "K9EventBus", DownBus)
    gate = next(iter(hil_gateway.GATE_TOPICS))
    with pytest.raises(GateTaskPublishError, match="was not published"):
        hil_gateway.publish_gate_task({}, gate, "JOB-1", title="t", description="d",
                                      source_orchestrator="X", source_topic="das.x",
                                      payload={}, artifacts=[])


def test_a_failed_read_does_not_erase_the_days_alert_log(store, monkeypatch):
    from k9_aif_abb.k9_core.messaging import k9_event_bus

    class Bus:
        def __init__(self, *a, **k):
            self._producer = None

        def publish(self, e):
            pass

        def close(self):
            pass

    monkeypatch.setattr(k9_event_bus, "K9EventBus", Bus)
    first = hil_gateway.record_governance_alert({}, {"type": "governance_hold", "job_id": "JOB-1"})
    key = (hil_gateway.STAGE_BUCKET, hil_gateway._alerts_key(first["at"][:10]))
    real_download = store["store"].download

    def flaky(bucket, k):
        raise ConnectionError("read timed out")

    store["store"].download = flaky
    with pytest.raises(StageStoreError, match="not listed"):
        hil_gateway.record_governance_alert({}, {"type": "governance_override", "job_id": "JOB-1"})
    store["store"].download = real_download
    day = json.loads(store["store"].objects[key].decode("utf-8"))
    assert [a["type"] for a in day] == ["governance_hold"]       # the earlier alert is still there


def test_every_subscribed_topic_has_its_orchestrator_and_drift_goes_to_traceability():
    from k9_dow.routers.das_router import DAS_TOPICS
    from k9_dow.runtime import dow_orchestrator_process as proc
    assert proc.TOPIC_ORCHESTRATOR["drift"] == "traceability"
    assert set(proc.DOMAIN_TOPICS) == {DAS_TOPICS[k] for k in proc.TOPIC_ORCHESTRATOR}
    assert set(proc.TOPIC_ORCHESTRATOR.values()) == {"requirement", "msa", "tmrr", "traceability"}
