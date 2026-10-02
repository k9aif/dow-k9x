# SPDX-License-Identifier: Apache-2.0
# K9-AIF Framework
"""DAS ↔ K9X HIL gate round trip.

A stage that ends at a non-delegable gate publishes a HIL task
(``publish_gate_task``). K9X HIL publishes the human decision to the gate's
reply topic (HIL v1.2.0+, transactional outbox). The DAS Router process
consumes those reply topics and turns an approval into a ``gate_approved``
event, which DasRouter routes to the next stage's topic:

    JCIDS ──▶ JROC-VALIDATION ──(approve)──▶ Acquisition
    Acquisition ──▶ PATHWAY-MILESTONE ──(approve)──▶ Systems Engineering

Stage outputs are kept in object storage by job id (``save_stage_result`` /
``load_stage_result``) because a decision can arrive days after the stage
that produced the package, in a different process.
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any, Dict, List, Optional

log = logging.getLogger(__name__)

# gate_id → where its HIL task goes and where HIL publishes the decision
GATE_TOPICS: Dict[str, Dict[str, str]] = {
    "JROC-VALIDATION": {"task_topic": "workflow.hil.das.jroc", "reply_topic": "das.jroc.replies"},
    "PATHWAY-MILESTONE": {"task_topic": "workflow.hil.das.pathway", "reply_topic": "das.pathway.replies"},
}
REPLY_TOPIC_TO_GATE: Dict[str, str] = {v["reply_topic"]: k for k, v in GATE_TOPICS.items()}

STAGE_BUCKET = "jcids-output"


def _broker(config: Dict[str, Any]) -> str:
    raw = (os.environ.get("KAFKA_BOOTSTRAP_SERVERS")
           or config.get("messaging", {}).get("bootstrap_servers", "localhost:9092"))
    return raw.split(",")[0].strip()


def publish_gate_task(
    config: Dict[str, Any],
    gate_id: str,
    job_id: str,
    *,
    title: str,
    description: str,
    source_orchestrator: str,
    source_topic: str,
    payload: Dict[str, Any],
    artifacts: List[str],
    priority: str = "high",
    ttl_hours: int = 168,
    ttl_action: str = "reject",
) -> bool:
    """Publish one HIL task for ``gate_id``. The decision comes back on the
    gate's reply topic, correlated by ``job_id``. Never raises: a failed
    publish is logged and reported as False (the stage result is kept)."""
    topics = GATE_TOPICS[gate_id]
    task = {
        "title": title,
        "description": description,
        "source_orchestrator": source_orchestrator,
        "source_topic": source_topic,
        "reply_to": topics["reply_topic"],
        "correlation_id": job_id,
        "priority": priority,
        "payload": {"job_id": job_id, "gate_id": gate_id, **payload},
        "artifacts": [a for a in artifacts if a],
        "pii": False,
        "ttl_hours": ttl_hours,
        "ttl_action": ttl_action,
    }
    try:
        from k9_aif_abb.k9_core.messaging.k9_event_bus import K9EventBus
        bus = K9EventBus(broker_url=_broker(config), topic=topics["task_topic"],
                         group_id=f"das-gate-{gate_id.lower()}")
        bus.publish(task)
        if bus._producer:
            bus._producer.flush()
        bus.close()
        log.info("[HILGateway] %s task published for job=%s → %s (reply_to=%s)",
                 gate_id, job_id, topics["task_topic"], topics["reply_topic"])
        return True
    except Exception as exc:
        log.warning("[HILGateway] %s task publish failed for job=%s (non-fatal): %s", gate_id, job_id, exc)
        return False


def gate_approved_event(gate_id: str, reply: Dict[str, Any]) -> Dict[str, Any]:
    """HIL decision (approve) → the DAS event DasRouter routes to the next stage."""
    job_id = reply.get("correlation_id", "")
    return {
        "event_type": "gate_approved",
        "gate_id": gate_id,
        "job_id": job_id,
        "correlation_id": job_id,
        "decision": {k: reply.get(k) for k in ("action", "actor", "comment", "decided_at", "status")},
    }


def approvers() -> Optional[set]:
    """DAS_HIL_APPROVERS (comma-separated emails). Unset = any HIL decision is
    accepted (public demo). Note the actor comes from K9X HIL's record."""
    raw = os.environ.get("DAS_HIL_APPROVERS", "").strip()
    return {a.strip().lower() for a in raw.split(",") if a.strip()} or None


# ── Stage results by job id ─────────────────────────────────────────

def _stage_key(job_id: str, stage: str) -> str:
    return f"by-job/{job_id}/{stage}.json"


def save_stage_result(config: Dict[str, Any], job_id: str, stage: str, result: Dict[str, Any]) -> Optional[str]:
    try:
        from k9_aif_abb.k9_factories.object_storage_factory import ObjectStorageFactory
        store = ObjectStorageFactory.create(config)
        key = _stage_key(job_id, stage)
        store.upload(STAGE_BUCKET, key, json.dumps(result, indent=2, default=str).encode("utf-8"))
        return store.get_uri(STAGE_BUCKET, key)
    except Exception as exc:
        log.warning("[HILGateway] saving %s result for job=%s failed (non-fatal): %s", stage, job_id, exc)
        return None


# The stage whose stored package a gate's decision resumes from.
GATE_INPUT_STAGE = {"JROC-VALIDATION": "jcids", "PATHWAY-MILESTONE": "acquisition"}


def stage_result_exists(config: Dict[str, Any], job_id: str, stage: str) -> bool:
    """A decision only resumes a job whose package was stored by this code.
    Reply topics are read from the earliest offset, so this also keeps old
    decisions (jobs from before the round trip existed) from starting runs."""
    try:
        from k9_aif_abb.k9_factories.object_storage_factory import ObjectStorageFactory
        return ObjectStorageFactory.create(config).exists(STAGE_BUCKET, _stage_key(job_id, stage))
    except Exception as exc:
        log.warning("[HILGateway] checking %s result for job=%s failed: %s", stage, job_id, exc)
        return False


def load_stage_result(config: Dict[str, Any], job_id: str, stage: str) -> Optional[Dict[str, Any]]:
    try:
        from k9_aif_abb.k9_factories.object_storage_factory import ObjectStorageFactory
        store = ObjectStorageFactory.create(config)
        return json.loads(store.download(STAGE_BUCKET, _stage_key(job_id, stage)).decode("utf-8"))
    except Exception as exc:
        log.warning("[HILGateway] loading %s result for job=%s failed: %s", stage, job_id, exc)
        return None
