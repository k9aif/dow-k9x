#!/usr/bin/env bash
# Run this on the Podman host (same box that runs the DAS pod).
#
# Fixes: DAS orchestrator/router health checks fail with
#   "Ollama <host>:11434 - [Errno 111] Connection refused"
# Root cause: `ollama serve` binds to 127.0.0.1:11434 by default. Any
# check run locally on this box (ollama ps, curl localhost:11434) still
# succeeds over loopback, which masks the problem -- only a remote
# caller (the DAS pod, or any other container) actually sees the refusal.
#
# After running this, restart the DAS pod separately:
#   podman play kube ubuntu/das-pod.yaml --replace

set -euo pipefail

OVERRIDE_DIR="/etc/systemd/system/ollama.service.d"
OVERRIDE_FILE="$OVERRIDE_DIR/override.conf"

echo "Current bind:"
ss -tlnp | grep 11434 || echo "  (nothing listening on 11434)"

sudo mkdir -p "$OVERRIDE_DIR"
sudo tee "$OVERRIDE_FILE" > /dev/null <<'EOF'
[Service]
Environment="OLLAMA_HOST=0.0.0.0:11434"
EOF

sudo systemctl daemon-reload
sudo systemctl restart ollama

echo "New bind:"
ss -tlnp | grep 11434

if ss -tlnp | grep 11434 | grep -qE '\*:11434|0\.0\.0\.0:11434'; then
  echo "OK: Ollama is listening on all interfaces."
else
  echo "STILL WRONG: not bound to 0.0.0.0 -- check for a conflicting Environment= line elsewhere (e.g. ~/.bashrc, another drop-in) that runs after this one."
  exit 1
fi
