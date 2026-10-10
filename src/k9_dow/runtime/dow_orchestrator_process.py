# SPDX-License-Identifier: Apache-2.0
# DoW Architecture Workbench — Orchestrator Process (Process 3 of 3)
#
# Async Kafka consumer that reads from DAS domain topics,
# dispatches each event to the correct orchestrator, and
# publishes results to das.results.
#
# Usage:
#   python -m k9_dow.runtime.dow_orchestrator_process

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
from k9_dow.orchestrators.requirement_orchestrator import RequirementOrchestrator
from k9_dow.orchestrators.msa_orchestrator import MsaOrchestrator
from k9_dow.orchestrators.tmrr_orchestrator import TmrrOrchestrator
from k9_dow.orchestrators.traceability_orchestrator import TraceabilityOrchestrator
from k9_dow.routers.das_router import DAS_TOPICS
from k9_dow.gates.hil_gateway import JobWithdrawn, withdrawn
from k9_dow.config.instance import group as _group

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(name)s — %(message)s",
)
log = logging.getLogger("dow.orchestrator_process")

DOMAIN_TOPICS = [DAS_TOPICS[k] for k in ("requirement", "mdd_package", "msa", "tmrr", "traceability", "drift")]
RESULTS_TOPIC = DAS_TOPICS["results"]
GROUP_ID = _group("dow-orchestrator")


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
    log.info("DAS Orchestrator — dependency check:")
    if not check_dependencies(config, require_kafka=True):
        log.error("Required dependencies are not available — aborting.")
        return


    brokers_raw = (
        os.environ.get("KAFKA_BOOTSTRAP_SERVERS")
        or config.get("messaging", {}).get("bootstrap_servers", "localhost:9092")
    )
    brokers = [b.strip() for b in brokers_raw.split(",") if b.strip()]
    broker = brokers[0]

    results_bus = K9EventBus(
        broker_url=broker,
        topic=RESULTS_TOPIC,
        group_id=GROUP_ID,
    )

    # Tracks the job_id of whichever execute_flow() call is currently in
    # flight. Safe as plain shared state (not per-task/contextvar) because
    # K9EventBus.subscribe_async awaits each handle() call to completion
    # before consuming the next Kafka message -- exactly one job runs at a
    # time in this process, confirmed by reading that consumer loop directly.
    _current_job = {"job_id": None}

    def _publish_progress(evt: dict) -> None:
        # Orchestrator _emit() calls (SquadStarted/SquadCompleted/etc.) and
        # the framework's LLMCall trace hook both funnel through here without
        # a job_id of their own -- tag it now so session-scoped SSE filtering
        # in the UI can tell which job's browser tab an event belongs to.
        if _current_job["job_id"] and "job_id" not in evt:
            evt = {**evt, "job_id": _current_job["job_id"]}
        try:
            results_bus.publish(evt)
            if results_bus._producer:
                results_bus._producer.flush()
        except Exception as exc:
            log.warning("[OrchestratorProcess] Progress publish failed: %s", exc)

    # Wire LLM call trace → das.results so UI shows them live
    from k9_aif_abb.k9_utils.llm_invoke import register_trace_callback
    register_trace_callback(_publish_progress)

    requirement_orch = RequirementOrchestrator(config=config, progress_callback=_publish_progress)
    msa_orch = MsaOrchestrator(config=config, progress_callback=_publish_progress)
    tmrr_orch = TmrrOrchestrator(config=config, progress_callback=_publish_progress)
    trace_orch = TraceabilityOrchestrator(config=config)

    # Topic → orchestrator. The MSA orchestrator owns two runs (MDD package, MSA).
    handlers = {
        DAS_TOPICS["requirement"]: requirement_orch,
        DAS_TOPICS["mdd_package"]: msa_orch,
        DAS_TOPICS["msa"]: msa_orch,
        DAS_TOPICS["tmrr"]: tmrr_orch,
        DAS_TOPICS["traceability"]: trace_orch,
    }

    log.info(
        "[OrchestratorProcess] Ready | handlers=%d | broker=%s",
        len(handlers), broker,
    )

    inbound_bus = K9EventBus(
        broker_url=broker,
        topic=DOMAIN_TOPICS[0],
        group_id=GROUP_ID,
    )

    async def handle(payload: dict) -> None:
        event_type = payload.get("event_type", "")
        corr = payload.get("correlation_id", "")
        topic = payload.get("_topic", "")

        # `_topic` is stamped by the DAS Router process (the run it routed to);
        # gate_approved events resume a later run, so event_type alone can't pick it.
        orch = handlers.get(topic) or requirement_orch

        orch_name = orch.__class__.__name__
        print(
            f"\n  ◀ ORCHESTRATOR  CONSUME  event_type='{event_type}'  → {orch_name}  corr={corr}\n",
            flush=True,
        )

        _current_job["job_id"] = payload.get("job_id")
        try:
            loop = asyncio.get_event_loop()
            wd = await loop.run_in_executor(None, withdrawn, config, payload.get("job_id"))
            if wd:
                raise JobWithdrawn(f"withdrawn by {wd.get('by')} at {wd.get('at')}")
            result = await loop.run_in_executor(None, orch.execute_flow, payload)
            status = result.get("status", "?")
            print(
                f"  ✓ ORCHESTRATOR  DONE  {orch_name}  status='{status}'  →  '{RESULTS_TOPIC}'\n",
                flush=True,
            )
            job_id = result.get("job_id") or payload.get("job_id", "")
            results_bus.publish({
                "event_type": event_type,
                "job_id": job_id,
                "correlation_id": corr,
                "orchestrator": orch_name,
                "result": result,
            })
        except JobWithdrawn as exc:
            # The job was withdrawn before or while this stage ran: it stops here.
            print(f"  ■ ORCHESTRATOR  WITHDRAWN  {orch_name}  job={payload.get('job_id')}  ({exc})\n", flush=True)
            results_bus.publish({
                "event_type": event_type,
                "job_id": payload.get("job_id", ""),
                "correlation_id": corr,
                "orchestrator": orch_name,
                "result": {"status": "withdrawn", "detail": str(exc), "job_id": payload.get("job_id", "")},
            })
        except Exception as exc:
            log.error(
                "[OrchestratorProcess] Pipeline error %s event_type=%s: %s",
                orch_name, event_type, exc, exc_info=True,
            )
            results_bus.publish({
                "event_type": event_type,
                "job_id": payload.get("job_id", ""),
                "correlation_id": corr,
                "orchestrator": orch_name,
                "result": {"status": "error", "detail": str(exc)},
            })
        finally:
            _current_job["job_id"] = None

    log.info(
        "[OrchestratorProcess] Starting K9EventBus async consumer on %d domain topics …",
        len(DOMAIN_TOPICS),
    )
    try:
        await inbound_bus.subscribe_async(
            handle,
            topics=DOMAIN_TOPICS,
            session_timeout_ms=60000,
            heartbeat_interval_ms=20000,
            max_poll_interval_ms=600000,
        )
    finally:
        results_bus.close()
        log.info("[OrchestratorProcess] Shutdown complete.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info("[OrchestratorProcess] Shutdown requested.")
    except Exception as exc:
        log.error("[OrchestratorProcess] Fatal: %s", exc, exc_info=True)
