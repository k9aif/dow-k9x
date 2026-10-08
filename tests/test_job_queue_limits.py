# SPDX-License-Identifier: Apache-2.0
"""Shared job queue: at most MAX_QUEUE_SIZE active jobs overall and MAX_JOBS_PER_SESSION per visitor,
so one visitor cannot fill the queue and lock everyone else out of the public demo."""

import asyncio
import json

import pytest


@pytest.fixture()
def app_mod(monkeypatch):
    from k9_dow.api import app as app_mod

    class FakeSQS:
        def send_message(self, **kw):
            pass

    monkeypatch.setattr(app_mod, "_require_llm", lambda: None)
    monkeypatch.setattr(app_mod, "_get_sqs_client", lambda: FakeSQS())
    monkeypatch.setattr(app_mod, "_get_or_create_queue_url", lambda sqs: "queue-url")
    monkeypatch.setattr(app_mod, "_job_store", {})
    monkeypatch.setattr(app_mod, "MAX_QUEUE_SIZE", 5)
    monkeypatch.setattr(app_mod, "MAX_JOBS_PER_SESSION", 2)
    return app_mod


def submit(app_mod, session):
    resp = asyncio.run(app_mod._submit_job("F22.md", "text", "capability_gap", session))
    return resp.status_code, json.loads(resp.body)


def test_a_visitor_may_hold_two_active_jobs(app_mod):
    assert submit(app_mod, "visitor-a")[0] == 200
    assert submit(app_mod, "visitor-a")[0] == 200
    code, body = submit(app_mod, "visitor-a")
    assert code == 429 and "2 per visitor" in body["error"]


def test_another_visitor_still_gets_in(app_mod):
    submit(app_mod, "visitor-a"), submit(app_mod, "visitor-a")
    assert submit(app_mod, "visitor-b")[0] == 200


def test_finished_jobs_do_not_count(app_mod):
    submit(app_mod, "visitor-a"), submit(app_mod, "visitor-a")
    for job in app_mod._job_store.values():
        job["status"] = "complete"
    assert submit(app_mod, "visitor-a")[0] == 200


def test_submissions_without_a_session_share_one_allowance(app_mod):
    assert submit(app_mod, "")[0] == 200
    assert submit(app_mod, "")[0] == 200
    assert submit(app_mod, "")[0] == 429


def test_the_overall_limit_still_applies(app_mod):
    for visitor in ("v1", "v1", "v2", "v2", "v3"):
        assert submit(app_mod, visitor)[0] == 200
    code, body = submit(app_mod, "v4")
    assert code == 429 and "queue is full" in body["error"]
