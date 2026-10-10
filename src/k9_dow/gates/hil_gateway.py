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
# Governance hold: not a policy gate. When k9x Shield or Granite Guardian refuses an agent's input in
# the middle of a run, the run is held (its state kept) and a person decides in K9X HIL whether to
# override that one check for that job and run, or stop the job.
GOVERNANCE_HOLD = "GOVERNANCE-HOLD"
GATE_TOPICS[GOVERNANCE_HOLD] = {"task_topic": "workflow.hil.das.governance-hold",
                                "reply_topic": "das.governance-hold.replies"}

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
    GOVERNANCE_HOLD: {"application": "DAS Governance", "queue": "Governance Holds",
                      "topic": "workflow.hil.das.governance-hold"},
}


# ── Governance alerts: every hold, override and rejection, one topic + a daily log ──

def alerts_topic() -> str:
    from k9_dow.config.instance import topic
    return topic("das.governance.alerts")


def _alerts_key(day: str) -> str:
    return f"{key_prefix()}governance/alerts/{day}.json"


def record_governance_alert(config: Dict[str, Any], alert: Dict[str, Any]) -> Dict[str, Any]:
    """Publish to the governance-alerts topic and append to that day's log (read by the admin's
    Governance page). Never raises: a failed publish or write is logged, the flow goes on."""
    from datetime import datetime, timezone
    alert = {"at": datetime.now(timezone.utc).isoformat(), **alert}
    try:
        from k9_aif_abb.k9_core.messaging.k9_event_bus import K9EventBus
        bus = K9EventBus(broker_url=_broker(config), topic=alerts_topic(), group_id=_group("das-governance-alerts"))
        bus.publish(alert)
        if bus._producer:
            bus._producer.flush()
        bus.close()
    except Exception as exc:
        log.warning("[HILGateway] governance alert publish failed (non-fatal): %s", exc)
    try:
        from k9_aif_abb.k9_factories.object_storage_factory import ObjectStorageFactory
        store = ObjectStorageFactory.create(config)
        key = _alerts_key(alert["at"][:10])
        try:
            day = json.loads(store.download(STAGE_BUCKET, key).decode("utf-8"))
        except Exception:
            day = []
        day.append(alert)
        store.upload(STAGE_BUCKET, key, json.dumps(day, indent=1, default=str).encode("utf-8"))
    except Exception as exc:
        log.warning("[HILGateway] governance alert log write failed (non-fatal): %s", exc)
    return alert


def governance_alerts(config: Dict[str, Any], start: str, end: str) -> List[Dict[str, Any]]:
    """Every governance alert from day ``start`` to ``end`` (YYYY-MM-DD, inclusive), newest first."""
    from datetime import date, timedelta
    from k9_aif_abb.k9_factories.object_storage_factory import ObjectStorageFactory
    store = ObjectStorageFactory.create(config)
    d0, d1 = date.fromisoformat(start), date.fromisoformat(end)
    out: List[Dict[str, Any]] = []
    for i in range(min((d1 - d0).days, 366) + 1):
        try:
            out += json.loads(store.download(STAGE_BUCKET, _alerts_key((d0 + timedelta(days=i)).isoformat())).decode("utf-8"))
        except Exception:
            continue
    return sorted(out, key=lambda a: a.get("at") or "", reverse=True)


def hold_check(reason: str) -> str:
    """The check a governance refusal names: '[InputSizeCheck]' in a Shield message, else Guardian."""
    import re
    m = re.search(r"\[(\w+)\]", reason or "")
    if m:
        return m.group(1)
    return "GraniteGuardian" if "Guardian" in (reason or "") else "k9x_Shield"


def hold_decision_current(hold: Dict[str, Any], decision: Optional[Dict[str, Any]]) -> bool:
    """A decision belongs to this hold only if it was made after the hold was raised."""
    return bool(decision) and (decision.get("decided_at") or "") >= (hold.get("at") or "")


def governance_override_event(config: Dict[str, Any], job_id: str, decision: Dict[str, Any]) -> Dict[str, Any]:
    """Approval of a governance hold → the held run, started again by its original approval, with
    the one check overridden (who, when, why) for this job and run only."""
    hold = load_stage_result(config, job_id, "hold") or {}
    return {
        "event_type": "gate_approved",
        "gate_id": hold.get("approved_gate"),
        "job_id": job_id,
        "correlation_id": job_id,
        "decision": hold.get("decision") or {},
        "governance_override": {"check": hold.get("check"), "run": hold.get("run"),
                                "reason": hold.get("reason"), "hold_at": hold.get("at"),
                                **{k: decision.get(k) for k in ("actor", "comment", "decided_at")}},
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
                                    GOVERNANCE_HOLD: "hold",
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


# ── Withdraw: stop a job and keep the record ────────────────────────

class JobWithdrawn(RuntimeError):
    """Raised before an agent runs when its job has been withdrawn."""


def withdraw_job(config: Dict[str, Any], job_id: str, by: str, reason: str = "") -> Dict[str, Any]:
    """Record the withdrawal. Every agent checks it before it starts (stage_base), so a
    running stage stops at its next agent; a queued job is never dispatched; a later HIL
    decision for this job is recorded but starts nothing."""
    from datetime import datetime, timezone
    rec = {"job_id": job_id, "by": by, "at": datetime.now(timezone.utc).isoformat(), "reason": reason[:500]}
    save_stage_result(config, job_id, "withdrawn", rec)
    return rec


def withdrawn(config: Dict[str, Any], job_id: Optional[str]) -> Optional[Dict[str, Any]]:
    return load_stage_result(config, job_id, "withdrawn") if job_id else None


def delete_job_data(config: Dict[str, Any], job_id: str) -> int:
    """Clean up a withdrawn job: delete its stored results and packages, keep the withdrawal
    record (who, when, why) so the job still shows as withdrawn."""
    from k9_aif_abb.k9_factories.object_storage_factory import ObjectStorageFactory
    store = ObjectStorageFactory.create(config)
    keep = _stage_key(job_id, "withdrawn")
    n = 0
    for key in store.list_objects(STAGE_BUCKET, prefix=f"{key_prefix()}by-job/{job_id}/") or []:
        if key != keep:
            store.delete(STAGE_BUCKET, key)
            n += 1
    return n


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


STALE_MINUTES = 20   # a run takes under 10 minutes on the reference GPU


def _stale(at: Optional[str]) -> bool:
    from datetime import datetime, timedelta, timezone
    if not at:
        return False
    try:
        t = datetime.fromisoformat(str(at).replace("Z", "+00:00"))
    except ValueError:
        return False
    if t.tzinfo is None:
        t = t.replace(tzinfo=timezone.utc)
    return datetime.now(timezone.utc) - t > timedelta(minutes=STALE_MINUTES)


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
            state = ("held" if rec and rec.get("status") == "held" else
                     "done" if rec and rec.get("status") not in (None, "error") else
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
        started = data.get(f"started-{nxt}") or {}
        failed_at = (data.get(nxt) or {}).get("failed_at") or ""
        if gate["state"] == "approved" and stage["state"] == "error" and (started.get("at") or "") > failed_at:
            stage["state"], stage["started_by"] = "running", started.get("by")     # retried, in progress
        elif gate["state"] == "approved" and stage["state"] == "error":
            stage["detail"] = (data.get(nxt) or {}).get("detail")
            next_action = {"gate": gate_id, "stage": nxt, "retry": True}
        elif gate["state"] == "approved" and stage["state"] == "not_reached":
            if started and _stale(started.get("at")):
                # Started long ago with no result: the run died without recording why.
                stage["detail"] = f"no result {STALE_MINUTES} minutes after it was started"
                next_action = {"gate": gate_id, "stage": nxt, "retry": True}
            elif started:
                stage["state"] = "running"
                stage["started_by"] = started.get("by")
            else:
                next_action = {"gate": gate_id, "stage": nxt}
    # Governance hold: a step right after the held run; approval offers the override re-run.
    hold = data.get("hold") if not legacy else None
    if hold:
        dec = data.get(f"gate-{GOVERNANCE_HOLD}")
        dec = dec if hold_decision_current(hold, dec) else None
        run_step = next((s for s in steps if s["step"] == hold.get("run")), None)
        hold_step = {"step": GOVERNANCE_HOLD, "kind": "gate", "hil": GATE_HIL_PLACE[GOVERNANCE_HOLD],
                     "detail": f"{hold.get('check')}: {hold.get('reason', '')}"[:300]}
        if dec:
            approved = dec.get("action") == "complete" and dec.get("accepted", True)
            hold_step.update(state="approved" if approved else (dec.get("action") or "decided"),
                             actor=dec.get("actor"), comment=dec.get("comment"), decided_at=dec.get("decided_at"))
        else:
            hold_step["state"] = "pending"
        if run_step is not None:
            steps.insert(steps.index(run_step) + 1, hold_step)
            started = data.get(f"started-{hold['run']}") or {}
            if run_step["state"] == "held" and hold_step["state"] == "approved":
                if (started.get("at") or "") > (dec.get("decided_at") or ""):
                    run_step["state"], run_step["started_by"] = "running", started.get("by")
                else:
                    next_action = {"gate": GOVERNANCE_HOLD, "stage": hold["run"], "override": hold.get("check")}
    complete = not legacy and any(s["step"] == "SE-REVIEW-SRR" and s["state"] == "approved" for s in steps)
    out_withdrawn = data.get("withdrawn")
    if out_withdrawn:
        # Nothing runs after a withdrawal: a running stage shows as stopped, no next action.
        next_action = None
        open_steps = [s for s in steps if s["state"] in ("running", "pending")]
        for s in open_steps or [next((x for x in steps if x["state"] == "not_reached"), None)]:
            if s:
                s["state"] = "withdrawn"
    return {
        "withdrawn": out_withdrawn,
        "job_id": job_id,
        "process_model": "jcids-legacy" if legacy else _PM.id,
        "document_title": first.get("document_title"),
        "filename": first.get("filename"),
        "steps": steps,
        "next_action": next_action,
        "complete": complete,
    }
