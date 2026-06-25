#!/bin/bash
# DoW Architecture Workbench — Start Router Process
# Process 2 of 3
#
# Consumes from: router.in
# Publishes to:  orchestrator.in / jcids.in / se.in / console.out
#
# Classifies documents, stores in S3, routes to correct pipeline topic.

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

source .env 2>/dev/null || true

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  DoW Architecture Workbench — Router"
echo "  Listening on: router.in"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Kafka:   ${KAFKA_BOOTSTRAP_SERVERS:-localhost:9092}"
echo "  Ollama:  ${OLLAMA_HOST:-http://localhost:11434}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

python -m k9_dow.runtime.dow_router_process
