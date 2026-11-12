# SPDX-License-Identifier: Apache-2.0
# K9-AIF Framework
"""Unit tests run in the test environment (most build agents with a minimal
config on purpose). Production governance with the real DAS config is tested
explicitly in test_governance.py."""

import os

os.environ.setdefault("K9_ENV", "test")

# Tests never reach live systems. DAS's settings load dow-k9-aif/.env on import, and on a developer machine
# that file holds the live endpoints (a red-team test wrote a job record "j" into the hosted DAS's storage,
# 2026-11-12). .env does not override variables already set, so these dead local endpoints win: a test that
# touches storage, Kafka or Postgres by accident fails instead of writing to production.
for _key, _value in {"S3_ENDPOINT_URL": "http://127.0.0.1:9", "KAFKA_BOOTSTRAP_SERVERS": "127.0.0.1:9",
                     "POSTGRES_HOST": "127.0.0.1", "POSTGRES_PORT": "9", "VECTORDB_HOST": "127.0.0.1",
                     "VECTORDB_PORT": "9", "DAS_INSTANCE": "test", "DAS_QUEUE_ENDPOINT": "http://127.0.0.1:9"}.items():
    os.environ[_key] = _value
