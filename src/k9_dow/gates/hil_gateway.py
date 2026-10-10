# SPDX-License-Identifier: Apache-2.0
# K9-AIF Framework
"""DAS ↔ K9X HIL gate round trip.

A run that ends at a non-delegable gate publishes a HIL task
(``publish_gate_task``). K9X HIL publishes the human decision to the gate's
reply topic (HIL v1.2.0+, transactional outbox). The DAS Router process
consumes those reply topics and turns an approval into a ``gate_approved``
event, which DasRouter routes to the next run's topic. Gates, topics and the
run each approval starts come from the process model (config/process_model.yaml):

    requirement ─▶ SERVICE-VALIDATION ─(approve)─▶ mdd_package ─▶ MDD ─(approve)─▶ msa
        └─▶ JCI-REVIEW (parallel; decision recorded)      msa ─▶ MILESTONE-A ─(approve)─▶ tmrr
                                                          tmrr ─▶ SE-REVIEW-SRR ─(approve)─▶ complete

Run results are kept in object storage by job id (``save_stage_result`` /
``load_stage_result``) because a decision can arrive days after the run that
produced the package, in a different process. JCIDS-era jobs (jcids →
JROC-VALIDATION → acquisition → PATHWAY-MILESTONE → se) still display in the
history and their late decisions are recorded, but they start no run.
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any, Dict, List, Optional

log = logging.getLogger(__name__)

from k9_dow.config.instance import group as _group, key_prefix
from k9_dow.config.process_model import load_process_model

_PM = load_process_model()

# JCIDS-era gates: their decisions are still recorded (jobs in flight at the switch), never resumed.
LEGACY_GATE_TOPICS: Dict[str, Dict[str, str]] = {
    "JROC-VALIDATION": {"task_topic": "workflow.hil.das.jroc", "reply_topic": "das.jroc.replies"},
    "PATHWAY-MILESTONE": {"task_topic": "workflow.hil.das.pathway", "reply_topic": "das.pathway.replies"},
}

# gate_id → where its HIL task goes and where HIL publishes the decision
GATE_TOPICS: Dict[str, Dict[str, str]] = {
    **LEGACY_GATE_TOPICS,
    **{g.id: {"task_topic": g.task_topic, "reply_topic": g.reply_topic} for g in _PM.gates.values()},
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
                         group_id=_group(f"das-gate-{gate_id.lower()}"))
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


# Where each gate's task appears in K9X HIL (application › queue).
GATE_HIL_PLACE: Dict[str, Dict[str, str]] = {
    "JROC-VALIDATION": {"application": "JCIDS", "queue": "JROC Review", "topic": "workflow.hil.das.jroc"},
    "PATHWAY-MILESTONE": {"application": "Acquisition", "queue": "Pathway Milestone Review",
                          "topic": "workflow.hil.das.pathway"},
    **{g.id: {"application": g.hil_application, "queue": g.hil_queue_name, "topic": g.task_topic}
       for g in _PM.gates.values()},
}

# Run each gate's approval starts (gates that start nothing are absent).
GATE_NEXT_STAGE: Dict[str, str] = {g.id: g.approval_starts for g in _PM.gates.values() if g.approval_starts}


def gate_decision_evidence(gate_id: str, decision: Dict[str, Any]) -> Dict[str, Any]:
    """The human decision at a gate, as evidence for the next stage's squad.

    It is the decision of record. The automated readiness assessment in the review package was
    input to that decision; without this item the next stage's agents see only that assessment
    and score "gate approved" from it, contradicting the human who approved."""
    if not decision:
        return {}
    action = decision.get("action")
    return {f"{gate_id} decision (human, of record)": {
        "gate": gate_id,
        "outcome": "APPROVED" if action == "complete" else str(action or "unknown").upper(),
        "decided_by": decision.get("actor"),
        "decided_at": decision.get("decided_at"),
        "comment": decision.get("comment"),
        "note": ("Decision of record by the human decision authority in K9X HIL. The automated "
                 "readiness assessment in the earlier review package was input to this decision "
                 "and is superseded by it."),
    }}


def resume_mode() -> str:
    """DAS_RESUME_MODE: "manual" (default) — a HIL approval is recorded and the
    DAS admin starts the next stage from Jobs in Pipeline; "auto" — the
    approval starts it immediately."""
    return "auto" if os.environ.get("DAS_RESUME_MODE", "manual").strip().lower() == "auto" else "manual"


def approvers() -> Optional[set]:
    """DAS_HIL_APPROVERS (comma-separated emails). Unset = any HIL decision is
    accepted (public demo). Note the actor comes from K9X HIL's record."""
    raw = os.environ.get("DAS_HIL_APPROVERS", "").strip()
    return {a.strip().lower() for a in raw.split(",") if a.strip()} or None


# ── Stage results by job id ─────────────────────────────────────────

def _stage_key(job_id: str, stage: str) -> str:
    return f"{key_prefix()}by-job/{job_id}/{stage}.json"


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


# The run whose stored package a gate reviews (a decision is recorded only if it exists).
GATE_INPUT_STAGE: Dict[str, str] = {"JROC-VALIDATION": "jcids", "PATHWAY-MILESTONE": "acquisition",
                                    **{g.id: g.prepared_by for g in _PM.gates.values()}}


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


# ── Job history (survives app restarts; read by the UI's Jobs tab) ──

LEGACY_STAGE_ORDER = ["jcids", "gate-JROC-VALIDATION", "acquisition", "gate-PATHWAY-MILESTONE", "se"]


def _process_stage_order() -> List[str]:
    """Runs and gates in order: each run, then the gates it prepares (blocking first)."""
    order: List[str] = []
    for run in _PM.runs():
        order.append(run)
        gates = sorted(_PM.gates_prepared_by(run), key=lambda g: not g.blocking)
        order += [f"gate-{g.id}" for g in gates]
    return order


STAGE_ORDER = _process_stage_order()


def mark_started(config: Dict[str, Any], job_id: str, stage: str, by: str) -> None:
    """Record that a stage was started, so it can't be started twice."""
    from datetime import datetime, timezone
    save_stage_result(config, job_id, f"started-{stage}",
                      {"by": by, "at": datetime.now(timezone.utc).isoformat()})


def save_gate_decision(config: Dict[str, Any], job_id: str, gate_id: str, decision: Dict[str, Any]) -> None:
    """Every HIL decision the Router receives (approve, reject, expire; accepted or not)."""
    save_stage_result(config, job_id, f"gate-{gate_id}", decision)


def list_job_ids(config: Dict[str, Any]) -> Dict[str, List[str]]:
    """job id → stored stage names, from object storage."""
    from k9_aif_abb.k9_factories.object_storage_factory import ObjectStorageFactory
    store = ObjectStorageFactory.create(config)
    jobs: Dict[str, List[str]] = {}
    for key in store.list_objects(STAGE_BUCKET, prefix=f"{key_prefix()}by-job/") or []:
        parts = key[len(key_prefix()):].split("/")
        if len(parts) == 3 and parts[2].endswith(".json"):
            jobs.setdefault(parts[1], []).append(parts[2][:-5])
    return jobs


def job_history(config: Dict[str, Any], job_id: str, stages: Optional[List[str]] = None) -> Dict[str, Any]:
    """Stage-by-stage view of one job: what ran, what each gate decided, what's pending."""
    stages = stages if stages is not None else list_job_ids(config).get(job_id, [])
    legacy = "jcids" in stages and "requirement" not in stages
    order = LEGACY_STAGE_ORDER if legacy else STAGE_ORDER
    data = {name: load_stage_result(config, job_id, name) for name in stages}
    first = data.get("jcids" if legacy else "requirement") or {}
    steps = []
    for name in order:
        rec = data.get(name)
        if name.startswith("gate-"):
            gate_id = name[5:]
            if not rec and legacy:
                # Decided before the Router kept decision files: the next stage
                # records the approval that started it.
                nxt, key = {"JROC-VALIDATION": ("acquisition", "jroc_decision"),
                            "PATHWAY-MILESTONE": ("se", "milestone_decision")}[gate_id]
                rec = (data.get(nxt) or {}).get(key) or None
            step = {"step": gate_id, "kind": "gate", "hil": GATE_HIL_PLACE.get(gate_id)}
            if not legacy and not _PM.gate(gate_id).blocking:
                step["parallel"] = True
            if rec:
                state = ("approved" if rec.get("action") == "complete" and rec.get("accepted", True)
                         else "ignored" if not rec.get("accepted", True) else rec.get("action") or "decided")
                steps.append({**step, "state": state, "actor": rec.get("actor"),
                              "comment": rec.get("comment"), "decided_at": rec.get("decided_at")})
            elif data.get(GATE_INPUT_STAGE[gate_id]):
                steps.append({**step, "state": "pending"})
            else:
                steps.append({**step, "state": "not_reached"})
        else:
            state = ("done" if rec and rec.get("status") not in (None, "error") else
                     "error" if rec else "not_reached")
            step = {"step": name, "kind": "stage", "state": state}
            if rec and rec.get("demo_stub"):
                step["demo"] = True
            steps.append(step)
    # What happens next: an approved gate whose next run hasn't started (current process only)
    next_action = None
    for gate_id, nxt in ({} if legacy else GATE_NEXT_STAGE).items():
        gate = next(s for s in steps if s["step"] == gate_id)
        stage = next(s for s in steps if s["step"] == nxt)
        if gate["state"] == "approved" and stage["state"] == "not_reached":
            started = data.get(f"started-{nxt}")
            if started:
                stage["state"] = "running"
                stage["started_by"] = started.get("by")
            else:
                next_action = {"gate": gate_id, "stage": nxt}
    complete = not legacy and any(s["step"] == "SE-REVIEW-SRR" and s["state"] == "approved" for s in steps)
    return {
        "job_id": job_id,
        "process_model": "jcids-legacy" if legacy else _PM.id,
        "document_title": first.get("document_title"),
        "filename": first.get("filename"),
        "steps": steps,
        "next_action": next_action,
        "complete": complete,
    }
