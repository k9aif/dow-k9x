#!/bin/bash
# DoW Architecture Workbench — Start App Backend (FastAPI + UI)
# Process 1 of 3
#
# Serves the web UI, handles document uploads, publishes to Kafka.
# Also the way to preview UI changes locally before a Podman build:
#   ./runit.sh  →  http://localhost:8000  (reloads on code changes; Ctrl+C stops)
# Uses .env, so a job started here runs on the Kafka/pipeline .env points at.

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

set -a; source .env 2>/dev/null || true; set +a
PY="${K9_PYTHON:-$HOME/ai/k9-aif-framework/.venv/bin/python}"
[ -x "$PY" ] || PY=python3

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  DoW Architecture Workbench — App Backend"
echo "  K9-AIF Framework SBB"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Ollama:  ${OLLAMA_HOST:-http://localhost:11434}"
echo "  Open:    http://localhost:${PORT:-8000}/"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

PYTHONPATH=src exec "$PY" -m uvicorn k9_dow.api.app:app --host 127.0.0.1 --port "${PORT:-8000}" --reload --reload-dir src
