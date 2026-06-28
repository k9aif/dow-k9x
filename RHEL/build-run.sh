#!/usr/bin/env bash
# K9-AIF DAS — Podman build and deploy helper
# Run from any directory on RHEL (no sudo needed — script handles it).
#
# Commands:
#   clone        — clone both repos from GitHub
#   build        — build the k9-aif-das container image
#   secret       — store secrets (Neo4j + Postgres passwords)
#   up           — deploy k9-dow-pod (3 containers)
#   down         — stop and remove the pod
#   status       — show pod and container status
#   logs         — tail app-backend logs
#   logs-router  — tail das-router logs
#   logs-orch    — tail das-orchestrator logs
#   all          — clone + build + secret + up in one step

set -euo pipefail

DEPLOY_DIR="${DAS_DEPLOY_DIR:-$HOME/ai/das-dev-pod-deployment}"
VOLUMES_DIR="/home/container_storage/volumes/das-dev"
FRAMEWORK_REPO="https://github.com/k9aif/k9-aif-framework.git"
DAS_REPO="https://github.com/k9aif/dow-k9x.git"
IMAGE="k9-aif-das:latest"
POD_NAME="k9-dow-pod"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

cmd="${1:-help}"

case "$cmd" in

  clone)
    echo "Cloning repos to $DEPLOY_DIR ..."
    mkdir -p "$DEPLOY_DIR"
    cd "$DEPLOY_DIR"

    if [[ -d "k9-aif-framework" ]]; then
      echo "  k9-aif-framework exists — pulling latest ..."
      cd k9-aif-framework && git pull && cd ..
    else
      git clone "$FRAMEWORK_REPO"
    fi

    if [[ -d "dow-k9-aif" ]]; then
      echo "  dow-k9-aif exists — pulling latest ..."
      cd dow-k9-aif && git pull && cd ..
    else
      git clone "$DAS_REPO" dow-k9-aif
    fi

    # Copy .env template if not present
    if [[ ! -f "dow-k9-aif/.env" ]]; then
      cat > "dow-k9-aif/.env" <<'ENVEOF'
K9_DOW_ENV=production
K9_ENV=production
OLLAMA_HOST=http://192.168.1.98:11434
OLLAMA_MODEL=granite3-dense:2b
KAFKA_BOOTSTRAP_SERVERS=192.168.1.98:9092
POSTGRES_HOST=192.168.1.98
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_DB=dow
K9_PG_PASSWORD=postgres
NEO4J_URI=bolt://192.168.1.98:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=neo4j!123
S3_ENDPOINT_URL=http://192.168.1.98:9000
AWS_ACCESS_KEY_ID=admin
AWS_SECRET_ACCESS_KEY=admin123
ENVEOF
      echo "  Created dow-k9-aif/.env — edit if needed"
    fi

    # Create volume dirs (same pattern as EOC)
    mkdir -p "$VOLUMES_DIR"/{config,data,logs,runtime}
    echo ""
    echo "Clone complete."
    echo "  $DEPLOY_DIR/k9-aif-framework/"
    echo "  $DEPLOY_DIR/dow-k9-aif/"
    echo "  $VOLUMES_DIR/ (config, data, logs, runtime)"
    ;;

  build)
    echo "Building $IMAGE from $DEPLOY_DIR ..."
    cd "$DEPLOY_DIR"
    sudo podman build -t "$IMAGE" \
      -f "dow-k9-aif/RHEL/Containerfile" \
      .
    echo "Build complete: $IMAGE"
    ;;

  secret)
    ENV_FILE="$DEPLOY_DIR/dow-k9-aif/.env"
    [[ -f "$ENV_FILE" ]] || { echo "Error: $ENV_FILE not found. Run 'clone' first."; exit 1; }

    # Neo4j password
    NEO4J_PW=$(grep -E '^NEO4J_PASSWORD=' "$ENV_FILE" | cut -d= -f2- | tr -d '[:space:]')
    if sudo podman secret exists neo4j-password 2>/dev/null; then
      sudo podman secret rm neo4j-password
    fi
    printf '%s' "$NEO4J_PW" | sudo podman secret create neo4j-password -
    echo "Secret 'neo4j-password' stored."

    # Postgres password
    PG_PW=$(grep -E '^K9_PG_PASSWORD=' "$ENV_FILE" | cut -d= -f2- | tr -d '[:space:]')
    if [[ -n "$PG_PW" ]]; then
      if sudo podman secret exists pg-password 2>/dev/null; then
        sudo podman secret rm pg-password
      fi
      printf '%s' "$PG_PW" | sudo podman secret create pg-password -
      echo "Secret 'pg-password' stored."
    else
      echo "Warning: K9_PG_PASSWORD not found in .env"
    fi
    ;;

  up)
    echo "Deploying pod: $POD_NAME (3 containers) ..."
    sudo podman play kube "$DEPLOY_DIR/dow-k9-aif/RHEL/das-pod.yaml" --replace
    echo ""
    echo "Pod running. Containers:"
    sudo podman ps --filter "pod=$POD_NAME" --format "table {{.Names}}\t{{.Status}}\t{{.Command}}"
    echo ""
    HOST_IP=$(hostname -I | awk '{print $1}')
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  DAS — Defense Acquisition System"
    echo "  Web UI:  http://${HOST_IP}:8000/"
    echo "  Health:  http://${HOST_IP}:8000/health"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "Logs:"
    echo "  sudo podman logs -f ${POD_NAME}-app-backend"
    echo "  sudo podman logs -f ${POD_NAME}-das-router"
    echo "  sudo podman logs -f ${POD_NAME}-das-orchestrator"
    ;;

  demo)
    echo "Starting DAS in demo mode (app-backend only, no router/orchestrator) ..."
    sudo podman run -d --rm \
      --name das-demo \
      -p 8000:8000 \
      --add-host rhel-host:192.168.1.98 \
      -e DEMO_MODE=ON \
      -e K9_ENV=development \
      -e KAFKA_BOOTSTRAP_SERVERS=rhel-host:9092 \
      -e OLLAMA_HOST=http://rhel-host:11434 \
      -e OLLAMA_MODEL=granite3-dense:2b \
      -e POSTGRES_HOST=rhel-host \
      -e POSTGRES_DB=dow \
      -e POSTGRES_USER=postgres \
      -e K9_PG_PASSWORD=postgres \
      "$IMAGE" \
      uvicorn k9_dow.api.app:app --host 0.0.0.0 --port 8000 --log-level info
    HOST_IP=$(hostname -I | awk '{print $1}')
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  DAS — Demo Mode (static sample output)"
    echo "  Web UI:  http://${HOST_IP}:8000/"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "  Stop:  sudo podman stop das-demo"
    ;;

  down)
    echo "Stopping pod: $POD_NAME ..."
    sudo podman stop das-demo 2>/dev/null || true
    sudo podman play kube "$DEPLOY_DIR/dow-k9-aif/RHEL/das-pod.yaml" --down || true
    echo "Pod stopped."
    ;;

  status)
    echo "=== Pod ==="
    sudo podman pod ps --filter "name=$POD_NAME"
    echo ""
    echo "=== Containers ==="
    sudo podman ps -a --filter "pod=$POD_NAME" \
      --format "table {{.Names}}\t{{.Status}}\t{{.RestartCount}}\t{{.Command}}"
    ;;

  logs)
    sudo podman logs -f "${POD_NAME}-app-backend"
    ;;

  logs-router)
    sudo podman logs -f "${POD_NAME}-das-router"
    ;;

  logs-orch)
    sudo podman logs -f "${POD_NAME}-das-orchestrator"
    ;;

  all)
    "$0" clone
    "$0" build
    "$0" secret
    "$0" up
    ;;

  help|*)
    echo "Usage: $0 <command>"
    echo ""
    echo "Commands:"
    echo "  clone        — clone k9-aif-framework + dow-k9-aif from GitHub"
    echo "  build        — build the Podman image ($IMAGE)"
    echo "  secret       — store passwords from .env as Podman secrets"
    echo "  up           — deploy $POD_NAME (3 containers)"
    echo "  down         — stop and remove the pod"
    echo "  status       — show pod and container status"
    echo "  logs         — tail app-backend logs"
    echo "  logs-router  — tail das-router logs"
    echo "  logs-orch    — tail das-orchestrator logs"
    echo "  all          — clone + build + secret + up in one step"
    ;;

esac
