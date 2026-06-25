# SPDX-License-Identifier: Apache-2.0
# DoW Architecture Workbench — DoDAF Orchestrator Runtime Process
#
# Kafka consumer on: dow.orchestrator.in
# Publishes to: dow.console.out / dow.results
#
# For each routed document event:
#   1. Runs DoDAF 6-stage pipeline (squads → agents → LLM)
#   2. Publishes stage progress to console.out
#   3. Publishes final results to dow.results

from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime, timezone

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer

from k9_dow.config.settings import settings
from k9_dow.orchestrators.dodaf_orchestrator import DodafOrchestrator

log = logging.getLogger("DoWOrchestrator")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(message)s")


async def _publish_console(producer, topic: str, job_id: str, stage_name: str,
                           status: str, message: str):
    await producer.send_and_wait(
        topic,
        json.dumps({
            "type": "console",
            "job_id": job_id,
            "stage_name": stage_name,
            "stage_status": status,
            "message": message,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }).encode("utf-8"),
    )


async def run_orchestrator():
    config = settings.load_yaml("config.yaml")
    messaging = config.get("messaging", {})
    broker = messaging.get("bootstrap_servers", "localhost:9092")
    topics = messaging.get("topics", {})

    orchestrator = DodafOrchestrator(config=config)

    consumer = AIOKafkaConsumer(
        topics.get("orchestrator_in", "dow.orchestrator.in"),
        bootstrap_servers=broker,
        group_id="dow_dodaf_orchestrator_v1",
        auto_offset_reset="latest",
        session_timeout_ms=60000,
        heartbeat_interval_ms=15000,
        max_poll_interval_ms=900000,
    )
    producer = AIOKafkaProducer(bootstrap_servers=broker)

    await producer.start()
    await consumer.start()

    console_topic = topics.get("console_out", "dow.console.out")
    results_topic = topics.get("results", "dow.results")

    log.info("[Orchestrator] Listening on %s", topics.get("orchestrator_in"))

    await _publish_console(
        producer, console_topic, "SYSTEM", "ORCHESTRATOR",
        "ready", "DoDAF Orchestrator is ready",
    )

    try:
        async for msg in consumer:
            try:
                event = json.loads(msg.value.decode("utf-8"))
            except Exception:
                continue

            job_id = event.get("job_id", "unknown")
            log.info("[Orchestrator] Processing job=%s", job_id)

            await _publish_console(
                producer, console_topic, job_id, "PIPELINE",
                "active", "DoDAF pipeline started",
            )

            # Run the pipeline synchronously (agents are sync)
            loop = asyncio.get_running_loop()
            result = await loop.run_in_executor(
                None,
                lambda: orchestrator.execute_flow({
                    "job_id": job_id,
                    "normalized_markdown": event.get("normalized_markdown", ""),
                    "routing_decision": event.get("routing_decision", {}),
                    "document_type": event.get("document_type", ""),
                }),
            )

            # Publish stage-by-stage progress
            for sr in result.get("stage_results", []):
                await _publish_console(
                    producer, console_topic, job_id,
                    f"Stage {sr.get('stage', '?')}",
                    sr.get("status", "unknown"),
                    f"Stage {sr.get('stage')} — {sr.get('squad_id')} — {sr.get('status')}",
                )

            # Publish final result
            await producer.send_and_wait(
                results_topic,
                json.dumps(result, default=str).encode("utf-8"),
            )

            status = result.get("status", "unknown")
            await _publish_console(
                producer, console_topic, job_id, "PIPELINE",
                "completed" if status == "completed" else "failed",
                f"DoDAF pipeline {status}",
            )

            log.info("[Orchestrator] Job %s %s", job_id, status)

    finally:
        await consumer.stop()
        await producer.stop()
        log.info("[Orchestrator] Stopped.")


if __name__ == "__main__":
    try:
        asyncio.run(run_orchestrator())
    except KeyboardInterrupt:
        log.info("Shutdown requested.")
