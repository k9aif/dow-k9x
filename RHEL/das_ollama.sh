#!/usr/bin/env bash
# Run this ON the PowerAI-5090 box (192.168.1.244), NOT on the RHEL host.
#
# Fixes: DAS orchestrator/router health checks fail with
#   "Ollama 192.168.1.244:11434 - [Errno 111] Connection refused"
# Root cause: `ollama serve` binds to 127.0.0.1:11434 by default. Any
# check run locally on this box (ollama ps, curl localhost:11434) still
# succeeds over loopback, which masks the problem -- only a remote
# caller (the RHEL-hosted DAS pod) actually sees the refusal.
#
# After running this, restart the DAS pod on the RHEL host separately:
#   podman play kube RHEL/das-pod.yaml --replace

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
