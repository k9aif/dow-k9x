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
from k9_dow.orchestrators.jcids_orchestrator import JcidsOrchestrator
from k9_dow.orchestrators.acquisition_orchestrator import AcquisitionOrchestrator
from k9_dow.orchestrators.se_orchestrator import SeOrchestrator
from k9_dow.orchestrators.traceability_orchestrator import TraceabilityOrchestrator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(name)s — %(message)s",
)
log = logging.getLogger("dow.orchestrator_process")

DOMAIN_TOPICS = [
    "das.jcids",
    "das.acquisition",
    "das.se",
    "das.traceability",
    "das.drift",
]
RESULTS_TOPIC = "das.results"
GROUP_ID = "dow-orchestrator"


def _load_config() -> dict:
    config_path = Path(__file__).resolve().parents[1] / "config" / "config.yaml"
    try:
        return load_yaml(config_path)
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

    def _publish_progress(evt: dict) -> None:
        try:
            results_bus.publish(evt)
            if results_bus._producer:
                results_bus._producer.flush()
        except Exception as exc:
            log.warning("[OrchestratorProcess] Progress publish failed: %s", exc)

    # Wire LLM call trace → das.results so UI shows them live
    from k9_aif_abb.k9_utils.llm_invoke import register_trace_callback
    register_trace_callback(_publish_progress)

    jcids_orch = JcidsOrchestrator(config=config, progress_callback=_publish_progress)
    acq_orch = AcquisitionOrchestrator(config=config)
    se_orch = SeOrchestrator(config=config)
    trace_orch = TraceabilityOrchestrator(config=config)

    handlers = {
        "das.jcids": jcids_orch,
        "das.acquisition": acq_orch,
        "das.se": se_orch,
        "das.traceability": trace_orch,
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

        orch = None
        for topic_prefix, orchestrator in handlers.items():
            if topic == topic_prefix or event_type.startswith(topic_prefix.split(".")[-1]):
                orch = orchestrator
                break

        if not orch:
            if "capability_gap" in event_type or "conops" in event_type:
                orch = jcids_orch
            else:
                orch = jcids_orch

        orch_name = orch.__class__.__name__
        print(
            f"\n  ◀ ORCHESTRATOR  CONSUME  event_type='{event_type}'  → {orch_name}  corr={corr}\n",
            flush=True,
        )

        try:
            loop = asyncio.get_event_loop()
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
