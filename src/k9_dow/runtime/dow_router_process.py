# SPDX-License-Identifier: Apache-2.0
# DoW Architecture Workbench — Router Runtime Process
#
# Kafka consumer on: dow.router.in
# Publishes to: dow.orchestrator.in / dow.jcids.in / dow.se.in / dow.console.out
#
# For each uploaded document event:
#   1. Fetches original file from S3
#   2. If .md/.txt → uses as-is; else → Docling normalization (optional)
#   3. Deterministic routing based on document_type
#   4. Publishes routed event to the correct pipeline topic

from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime, timezone

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError

from k9_dow.config.settings import settings
from k9_dow.routers.dow_document_router import DowDocumentRouter
from k9_dow.agents.src.document_normalization_agent import DocumentNormalizationAgent

log = logging.getLogger("DoWRouter")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(message)s")


def _ensure_topics(broker: str, topics: dict):
    try:
        admin = KafkaAdminClient(bootstrap_servers=broker)
        existing = set(admin.list_topics())
        needed = set(topics.values()) - existing
        if needed:
            admin.create_topics(
                [NewTopic(name=t, num_partitions=1, replication_factor=1) for t in needed]
            )
            log.info("[Router] Created topics: %s", ", ".join(needed))
        else:
            log.info("[Router] All topics exist.")
    except Exception as exc:
        log.warning("[Router] Topic check failed: %s", exc)


_ROUTE_TO_TOPIC = {
    "dodaf_pipeline": "orchestrator_in",
    "jcids_pipeline": "jcids_in",
    "se_pipeline": "se_in",
    "business_pipeline": "orchestrator_in",
    "unknown_pipeline": "orchestrator_in",
}


async def run_router():
    config = settings.load_yaml("config.yaml")
    messaging = config.get("messaging", {})
    broker = messaging.get("bootstrap_servers", "localhost:9092")
    topics = messaging.get("topics", {})

    _ensure_topics(broker, topics)

    router = DowDocumentRouter(config=config)
    normalizer = DocumentNormalizationAgent(config=config)

    consumer = AIOKafkaConsumer(
        topics.get("router_in", "dow.router.in"),
        bootstrap_servers=broker,
        group_id="dow_router_v1",
        auto_offset_reset="latest",
    )
    producer = AIOKafkaProducer(bootstrap_servers=broker)

    await producer.start()
    await consumer.start()

    log.info("[Router] Listening on %s at %s", topics.get("router_in"), broker)

    # Ready signal
    await producer.send_and_wait(
        topics.get("console_out", "dow.console.out"),
        json.dumps({
            "type": "console",
            "stage_name": "ROUTER",
            "stage_status": "ready",
            "message": "DoW Router is ready and listening for documents",
        }).encode("utf-8"),
    )

    try:
        async for msg in consumer:
            try:
                event = json.loads(msg.value.decode("utf-8"))
            except Exception:
                continue

            job_id = event.get("job_id", "unknown")
            log.info("[Router] Received event for job=%s", job_id)

            # Normalize
            norm_result = normalizer.execute({
                "source_markdown": event.get("text", ""),
                "metadata": event.get("metadata", {}),
            })
            normalized_md = norm_result.get("output") or norm_result.get("markdown") or event.get("text", "")

            # Route
            routing = router.route({
                "job_id": job_id,
                "filename": event.get("filename", ""),
                "markdown": normalized_md,
                "document_type": event.get("document_type", ""),
            })

            route_to = routing.get("route_to", "unknown_pipeline")
            dest_topic_key = _ROUTE_TO_TOPIC.get(route_to, "orchestrator_in")
            dest_topic = topics.get(dest_topic_key, "dow.orchestrator.in")

            out_event = {
                "job_id": job_id,
                "filename": event.get("filename"),
                "normalized_markdown": normalized_md,
                "routing_decision": routing,
                "document_type": event.get("document_type"),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            await producer.send_and_wait(
                dest_topic, json.dumps(out_event).encode("utf-8"),
            )

            log.info("[Router] Routed job=%s → %s (topic=%s)", job_id, route_to, dest_topic)

            await producer.send_and_wait(
                topics.get("console_out", "dow.console.out"),
                json.dumps({
                    "type": "console",
                    "job_id": job_id,
                    "stage_name": "ROUTER",
                    "stage_status": "completed",
                    "message": f"Routed to {route_to} (topic={dest_topic})",
                }).encode("utf-8"),
            )

    finally:
        await consumer.stop()
        await producer.stop()
        log.info("[Router] Stopped.")


if __name__ == "__main__":
    try:
        asyncio.run(run_router())
    except KeyboardInterrupt:
        log.info("Shutdown requested.")
