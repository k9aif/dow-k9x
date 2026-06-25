#!/bin/bash
# DoW Architecture Workbench — Start DoDAF Orchestrator Process
# Process 3 of 3
#
# Consumes from: orchestrator.in
# Publishes to:  console.out / dow-results
#
# Runs DoDAF 2.0 6-stage pipeline: squads → agents → LLM → governance.

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

source .env 2>/dev/null || true

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  DoW Architecture Workbench — DoDAF Orchestrator"
echo "  Listening on: orchestrator.in"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Kafka:   ${KAFKA_BOOTSTRAP_SERVERS:-localhost:9092}"
echo "  Ollama:  ${OLLAMA_HOST:-http://localhost:11434}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

python -m k9_dow.runtime.dow_orchestrator_process
