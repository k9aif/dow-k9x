#!/usr/bin/env python3
"""dow-k9-aif (DAS) — backing-service connectivity smoke test (Postgres,
Neo4j, Kafka, MinIO/S3). Reads connection details from .env, same as the
app itself. Run directly, no test framework needed:

    python3 tests/db_test.py

Exits 0 if every service is reachable, non-zero otherwise. Note: the
Postgres schema/tables aren't checked for existence here — the "dow"
schema and its 4 generic framework tables (sessions, session_turns,
routing_decisions, context_artifacts) only get created by
RoutingStateStore on the app's first real connection, so an empty
schema on a fresh deploy is expected, not a failure.
"""
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

results: list[tuple[str, bool, str]] = []


def check(name: str, fn) -> None:
    try:
        detail = fn()
        results.append((name, True, detail))
    except Exception as e:  # noqa: BLE001
        results.append((name, False, str(e)))


def check_postgres() -> str:
    import psycopg2

    host = os.environ.get("POSTGRES_HOST", "localhost")
    port = os.environ.get("POSTGRES_PORT", "5432")
    db = os.environ.get("POSTGRES_DB", "dow")
    user = os.environ.get("POSTGRES_USER", "postgres")
    password = os.environ.get("K9_PG_PASSWORD", "")

    conn = psycopg2.connect(host=host, port=port, user=user, password=password, dbname=db)
    try:
        cur = conn.cursor()
        cur.execute("SELECT version()")
        return f"{host}:{port}/{db} — {cur.fetchone()[0].split(',')[0]}"
    finally:
        conn.close()


def check_neo4j() -> str:
    from neo4j import GraphDatabase

    uri = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
    user = os.environ.get("NEO4J_USER", "neo4j")
    password = os.environ.get("NEO4J_PASSWORD", "")

    drv = GraphDatabase.driver(uri, auth=(user, password))
    try:
        drv.verify_connectivity()
        with drv.session() as session:
            r = session.run(
                "MATCH (n) WHERE n.id IS NOT NULL AND any(l IN labels(n) WHERE l IN "
                "['CapabilityNeed','CapabilityDocs','SERequirement','TechnicalBaselineItem',"
                "'DoDAFView','TestCase','VerificationEvent','FundingLine','SEPBaseline',"
                "'GateCriterion']) RETURN count(n) AS c"
            ).single()
            return f"{uri} — {r['c']} DAS traceability nodes present"
    finally:
        drv.close()


def check_kafka() -> str:
    from kafka import KafkaAdminClient

    broker = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    admin = KafkaAdminClient(bootstrap_servers=broker, client_id="dow-k9-aif-db-test")
    try:
        topics = admin.list_topics()
        return f"{broker} — {len(topics)} topics visible"
    finally:
        admin.close()


def check_minio() -> str:
    import boto3

    endpoint = os.environ.get("S3_ENDPOINT_URL", "http://localhost:9000")
    access_key = os.environ.get("AWS_ACCESS_KEY_ID", "")
    secret_key = os.environ.get("AWS_SECRET_ACCESS_KEY", "")
    s3 = boto3.client("s3", endpoint_url=endpoint, aws_access_key_id=access_key,
                       aws_secret_access_key=secret_key)
    buckets = [b["Name"] for b in s3.list_buckets()["Buckets"]]
    return f"{endpoint} — buckets: {buckets}"


def main() -> int:
    check("Postgres", check_postgres)
    check("Neo4j", check_neo4j)
    check("Kafka", check_kafka)
    check("MinIO", check_minio)

    ok = True
    for name, passed, detail in results:
        if passed:
            print(f"  PASS: {name} — {detail}")
        else:
            print(f"  FAIL: {name} — {detail}", file=sys.stderr)
            ok = False

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
