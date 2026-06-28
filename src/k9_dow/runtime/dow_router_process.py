# SPDX-License-Identifier: Apache-2.0
# DoW Architecture Workbench — Router Process (Process 2 of 3)
#
# Async Kafka consumer that routes events from dow.router.in
# to the correct pipeline topic via DasRouter.
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

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(name)s — %(message)s",
)
log = logging.getLogger("dow.router_process")

INBOUND_TOPIC = "dow.router.in"
GROUP_ID = "dow-router"


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
            group_id=f"dow-router-pub-{label}",
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

    log.info("[RouterProcess] Starting K9EventBus async consumer …")
    try:
        await inbound_bus.subscribe_async(handle)
    finally:
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
