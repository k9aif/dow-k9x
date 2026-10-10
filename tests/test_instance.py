# SPDX-License-Identifier: Apache-2.0
"""DAS_INSTANCE: unset leaves every name as it was; set gives the instance its own."""

import importlib


def test_unset_keeps_every_name(monkeypatch):
    monkeypatch.delenv("DAS_INSTANCE", raising=False)
    from k9_dow.config import instance
    assert instance.topic("dow.router.in") == "dow.router.in"
    assert instance.group("dow-router") == "dow-router"
    assert instance.key_prefix() == ""
    from k9_dow.gates import hil_gateway
    assert hil_gateway._stage_key("J", "requirement") == "by-job/J/requirement.json"


def test_next_instance_gets_its_own_names(monkeypatch):
    monkeypatch.setenv("DAS_INSTANCE", "next")
    from k9_dow.config import instance
    assert instance.topic("das.results") == "next.das.results"
    assert instance.group("das-job-queue") == "das-job-queue-next"
    from k9_dow.gates import hil_gateway
    assert hil_gateway._stage_key("J", "msa") == "next/by-job/J/msa.json"
    from k9_dow.routers import das_router
    importlib.reload(das_router)
    try:
        assert das_router.DAS_TOPICS["msa"] == "next.das.msa"
        # HIL is shared: gate task and reply topics are not renamed
        assert hil_gateway.GATE_TOPICS["MDD"]["reply_topic"] == "das.mdd.replies"
    finally:
        monkeypatch.delenv("DAS_INSTANCE")
        importlib.reload(das_router)


def test_list_job_ids_reads_only_this_instances_prefix(monkeypatch):
    monkeypatch.setenv("DAS_INSTANCE", "next")
    from k9_dow.gates import hil_gateway

    class Store:
        def list_objects(self, bucket, prefix=""):
            keys = ["by-job/LIVE/jcids.json", "next/by-job/N1/requirement.json", "next/by-job/N1/msa.json"]
            return [k for k in keys if k.startswith(prefix)]

    import k9_aif_abb.k9_factories.object_storage_factory as f
    monkeypatch.setattr(f.ObjectStorageFactory, "create", staticmethod(lambda cfg: Store()))
    assert hil_gateway.list_job_ids({}) == {"N1": ["requirement", "msa"]}
