#!/bin/bash
# DoW Architecture Workbench — Start App Backend (FastAPI + UI)
# Process 1 of 3
#
# Serves the web UI, handles document uploads, publishes to Kafka.

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

source .env 2>/dev/null || true

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  DoW Architecture Workbench — App Backend"
echo "  K9-AIF Framework SBB"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Ollama:  ${OLLAMA_HOST:-http://localhost:11434}"
echo "  Port:    8000"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

uvicorn k9_dow.api.app:app --host 0.0.0.0 --port 8000 --reload
