#!/usr/bin/env bash
# Preview DAS's web pages on this machine (no Podman build): http://localhost:8001
# Uses .env for settings. Pages and the UI are local; if you start a job here,
# it goes to the same Kafka as the deployed DAS and runs on that pipeline.
# Stop with Ctrl+C.
set -euo pipefail
cd "$(dirname "$0")"
PY="${K9_PYTHON:-$HOME/ai/k9-aif-framework/.venv/bin/python}"
set -a; [ -f .env ] && . ./.env; set +a
echo "DAS preview: http://localhost:${PORT:-8001}/  (app: /app)"
PYTHONPATH=src exec "$PY" -m uvicorn k9_dow.api.app:app --host 127.0.0.1 --port "${PORT:-8001}" --reload --reload-dir src
