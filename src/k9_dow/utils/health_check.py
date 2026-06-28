# SPDX-License-Identifier: Apache-2.0
# DAS — Startup dependency health checks

import logging
import os
import socket
from urllib.parse import urlparse

log = logging.getLogger("das.health")


def _check_tcp(host: str, port: int, label: str, timeout: float = 3.0) -> bool:
    try:
        sock = socket.create_connection((host, port), timeout=timeout)
        sock.close()
        log.info("  ✓ %s  %s:%d", label, host, port)
        return True
    except (socket.timeout, ConnectionRefusedError, OSError) as exc:
        log.error("  ✗ %s  %s:%d — %s", label, host, port, exc)
        return False


def check_dependencies(config: dict, require_kafka: bool = False) -> bool:
    results = []

    pg = config.get("postgres", {})
    pg_host = pg.get("host", "localhost")
    pg_port = int(pg.get("port", 5432))
    results.append(_check_tcp(pg_host, pg_port, "PostgreSQL"))

    ollama_url = (
        config.get("inference", {}).get("llm_factory", {}).get("base_url", "")
        or os.environ.get("OLLAMA_HOST", "http://localhost:11434")
    )
    parsed = urlparse(ollama_url)
    ollama_host = parsed.hostname or "localhost"
    ollama_port = parsed.port or 11434
    results.append(_check_tcp(ollama_host, ollama_port, "Ollama"))

    if require_kafka:
        kafka_raw = (
            os.environ.get("KAFKA_BOOTSTRAP_SERVERS")
            or config.get("messaging", {}).get("bootstrap_servers", "localhost:9092")
        )
        broker = kafka_raw.split(",")[0].strip()
        parts = broker.rsplit(":", 1)
        kafka_host = parts[0]
        kafka_port = int(parts[1]) if len(parts) > 1 else 9092
        results.append(_check_tcp(kafka_host, kafka_port, "Kafka"))

    s3_url = (
        os.environ.get("S3_ENDPOINT_URL")
        or config.get("object_storage", {}).get("s3", {}).get("endpoint_url", "")
    )
    if s3_url:
        parsed = urlparse(s3_url)
        s3_host = parsed.hostname or "localhost"
        s3_port = parsed.port or 9000
        results.append(_check_tcp(s3_host, s3_port, "S3/MinIO"))

    neo4j_uri = os.environ.get("NEO4J_URI", "")
    if neo4j_uri:
        parsed = urlparse(neo4j_uri.replace("bolt://", "http://"))
        neo4j_host = parsed.hostname or "localhost"
        neo4j_port = parsed.port or 7687
        results.append(_check_tcp(neo4j_host, neo4j_port, "Neo4j"))

    return all(results)
