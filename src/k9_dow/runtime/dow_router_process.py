# SPDX-License-Identifier: Apache-2.0
# DoW Architecture Workbench — Router Process (Process 2 of 3)
#
# Async Kafka consumer that routes events from dow.router.in
# to the correct pipeline topic via DasRouter.
#
# Also consumes the HIL gate reply topics (one per gate of the process model,
# config/process_model.yaml): K9X HIL publishes each human decision there, and an
# approval becomes a gate_approved event that DasRouter routes to the run that
# gate's approval starts. A gate that starts nothing (JCI-REVIEW, SE-REVIEW-SRR,
# JCIDS-era gates) is recorded only. Keeps the K9-AIF rule that only the Router
# publishes to domain topics. See gates/hil_gateway.py.
#
# Usage:
#   python -m k9_dow.runtime.dow_router_process

import asyncio
import logging
import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parents[3] / ".env", override=False)
except ImportError:
    pass

from k9_aif_abb.k9_utils.config_loader import load_yaml
from k9_aif_abb.k9_core.messaging.k9_event_bus import K9EventBus
from k9_dow.routers.das_router import DasRouter, DAS_TOPICS
from k9_dow.config.instance import group as _group, topic as _topic
from k9_dow.gates.hil_gateway import (GOVERNANCE_HOLD, governance_override_event, record_governance_alert)
from k9_dow.gates.hil_gateway import (GATE_INPUT_STAGE, GATE_TOPICS, approvers,
                                      gate_approved_event, mark_started, resume_mode,
                                      save_gate_decision, stage_result_exists, GATE_NEXT_STAGE)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(name)s — %(message)s",
)
log = logging.getLogger("dow.router_process")

INBOUND_TOPIC = _topic("dow.router.in")
GROUP_ID = _group("dow-router")


def _load_config() -> dict:
    config_path = Path(__file__).resolve().parents[1] / "config" / "config.yaml"
    try:
        from k9_dow.config.runtime import apply_runtime_settings
        return apply_runtime_settings(load_yaml(config_path))
    except Exception as exc:
        log.warning("Config load skipped: %s", exc)
        return {}


async def main() -> None:
    config = _load_config()

    from k9_dow.utils.health_check import check_dependencies
    log.info("DAS Router — dependency check:")
    if not check_dependencies(config, require_kafka=True):
        log.error("Required dependencies are not available — aborting.")
        return

    brokers_raw = (
        os.environ.get("KAFKA_BOOTSTRAP_SERVERS")
        or config.get("messaging", {}).get("bootstrap_servers", "localhost:9092")
    )
    brokers = [b.strip() for b in brokers_raw.split(",") if b.strip()]
    broker = brokers[0]

    router = DasRouter(config=config)
    log.info("[RouterProcess] Initialized | broker=%s | inbound=%s", broker, INBOUND_TOPIC)

    outbound_buses: dict[str, K9EventBus] = {}
    for label, topic in DAS_TOPICS.items():
        outbound_buses[topic] = K9EventBus(
            broker_url=broker,
            topic=topic,
            group_id=_group(f"dow-router-pub-{label}"),
        )

    inbound_bus = K9EventBus(
        broker_url=broker,
        topic=INBOUND_TOPIC,
        group_id=GROUP_ID,
    )

    async def handle(payload: dict) -> None:
        event_type = payload.get("event_type", "")
        corr = payload.get("correlation_id", "")
        log.info("[RouterProcess] Received event_type=%s corr=%s", event_type, corr)
        try:
            routed = router.route(payload)
            route_to = routed.get("route_to", "")
            classification = routed.get("classification", "")

            bus = outbound_buses.get(route_to)
            if bus:
                # The orchestrator process picks the stage by this tag
                # (the bus callback only sees the message value, not its topic).
                payload = {**payload, "_topic": route_to}
                bus.publish(payload)
                if bus._producer:
                    bus._producer.flush()
                print(
                    f"\n  ▶ ROUTER  PUBLISH  event_type='{event_type}'  →  topic='{route_to}'  ({classification})  corr={corr}\n",
                    flush=True,
                )
            else:
                log.warning("[RouterProcess] No outbound bus for topic=%s", route_to)
        except Exception as exc:
            log.error("[RouterProcess] Routing failed: %s", exc, exc_info=True)

    results_bus = outbound_buses[DAS_TOPICS["results"]]
    seen_decisions: set = set()  # (job_id, gate_id): HIL's outbox is at-least-once

    def _result_event(evt: dict) -> None:
        results_bus.publish(evt)
        if results_bus._producer:
            results_bus._producer.flush()

    def make_reply_handler(gate_id: str):
        async def handle_reply(reply: dict) -> None:
            job_id = reply.get("correlation_id", "")
            action = (reply.get("action") or "").lower()
            actor = (reply.get("actor") or "").lower()
            if not job_id or (job_id, gate_id) in seen_decisions:
                return
            seen_decisions.add((job_id, gate_id))
            loop = asyncio.get_event_loop()
            if not await loop.run_in_executor(
                    None, stage_result_exists, config, job_id, GATE_INPUT_STAGE[gate_id]):
                log.info("[RouterProcess] HIL decision gate=%s job=%s: no stored %s package, nothing to resume",
                         gate_id, job_id, GATE_INPUT_STAGE[gate_id])
                return
            allowed = approvers()
            accepted = allowed is None or actor in allowed
            await loop.run_in_executor(None, save_gate_decision, config, job_id, gate_id, {
                **{k: reply.get(k) for k in ("action", "actor", "comment", "decided_at", "status")},
                "gate_id": gate_id, "accepted": accepted})
            log.info("[RouterProcess] HIL decision gate=%s job=%s action=%s actor=%s accepted=%s",
                     gate_id, job_id, action, actor, accepted)
            _result_event({
                "type": "GateDecision", "job_id": job_id, "gate_id": gate_id,
                "action": action, "actor": reply.get("actor"), "comment": reply.get("comment"),
                "decided_at": reply.get("decided_at"), "accepted": accepted,
                "resume": resume_mode(),
            })
            if not accepted:
                return
            if gate_id == GOVERNANCE_HOLD:
                # A person decided a governance hold: alert, then resume with the override or stop.
                await loop.run_in_executor(None, record_governance_alert, config, {
                    "type": "governance_override" if action == "complete" else "governance_hold_rejected",
                    "job_id": job_id, "actor": reply.get("actor"), "comment": reply.get("comment"),
                    "decided_at": reply.get("decided_at")})
                if action == "complete" and resume_mode() == "auto":
                    event = await loop.run_in_executor(None, governance_override_event, config, job_id, reply)
                    await loop.run_in_executor(None, mark_started, config, job_id,
                                               event["governance_override"].get("run"), "auto")
                    await handle(event)
                elif action != "complete":
                    _result_event({"event_type": "gate_decision", "job_id": job_id, "correlation_id": job_id,
                                   "orchestrator": "DasRouter",
                                   "result": {"status": "stopped_at_gate", "gate_id": gate_id, "action": action,
                                              "actor": reply.get("actor"), "orchestrator": "router"}})
                return
            if action == "complete" and gate_id not in GATE_NEXT_STAGE:
                # Recorded above; nothing to start (parallel JCI review, final SRR, legacy gate).
                print(f"\n  ✔ HIL  {gate_id} decided by {reply.get('actor')}  job={job_id}  → recorded\n",
                      flush=True)
                if gate_id == "SE-REVIEW-SRR":
                    _result_event({
                        "event_type": "gate_decision", "job_id": job_id, "correlation_id": job_id,
                        "orchestrator": "DasRouter",
                        "result": {"status": "pipeline_complete", "gate_id": gate_id,
                                   "actor": reply.get("actor"), "orchestrator": "router"},
                    })
            elif action == "complete" and resume_mode() == "manual":
                # Recorded (gate file above); the DAS admin starts the next
                # stage from Jobs in Pipeline (POST /jobs/<id>/advance).
                print(f"\n  ✔ HIL  {gate_id} approved by {reply.get('actor')}  job={job_id}"
                      f"  → awaiting DAS admin to start the next stage\n", flush=True)
            elif action == "complete":
                print(f"\n  ✔ HIL  {gate_id} approved by {reply.get('actor')}  job={job_id}  → resuming\n",
                      flush=True)
                await loop.run_in_executor(None, mark_started, config, job_id,
                                           GATE_NEXT_STAGE[gate_id], "auto")
                await handle(gate_approved_event(gate_id, reply))
            elif gate_id in GATE_NEXT_STAGE or gate_id == "SE-REVIEW-SRR":
                # reject / expire on a blocking gate: the pipeline stops there. (A JCI-REVIEW
                # rejection is recorded above; it never holds the acquisition flow.)
                _result_event({
                    "event_type": "gate_decision", "job_id": job_id, "correlation_id": job_id,
                    "orchestrator": "DasRouter",
                    "result": {"status": "stopped_at_gate", "gate_id": gate_id, "action": action,
                               "actor": reply.get("actor"), "orchestrator": "router"},
                })
        return handle_reply

    reply_buses = [
        (K9EventBus(broker_url=broker, topic=t["reply_topic"], group_id=_group(f"dow-router-hil-{gate_id.lower()}")), gate_id)
        for gate_id, t in GATE_TOPICS.items()
    ]

    log.info("[RouterProcess] Starting K9EventBus async consumers (router.in + %d HIL reply topics) …",
             len(reply_buses))
    try:
        await asyncio.gather(
            inbound_bus.subscribe_async(handle),
            *(bus.subscribe_async(make_reply_handler(gate_id)) for bus, gate_id in reply_buses),
        )
    finally:
        for bus, _ in reply_buses:
            bus.close()
        for bus in outbound_buses.values():
            bus.close()
        log.info("[RouterProcess] Shutdown complete.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info("[RouterProcess] Shutdown requested.")
    except Exception as exc:
        log.error("[RouterProcess] Fatal: %s", exc, exc_info=True)
