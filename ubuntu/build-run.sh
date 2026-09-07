#!/usr/bin/env bash
# K9-AIF DAS — Podman build and deploy helper
# Run from any directory on the Podman host (no sudo needed — script handles it).
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

# `podman play kube`'s secretKeyRef resolution reads the Podman secret's
# raw content and unmarshals it as a full Kubernetes Secret manifest (not
# a bare value) — a secret created via `podman secret create name -` with
# just the plaintext password fails at deploy time with "not valid
# JSON/YAML ... cannot unmarshal string into Go value of type v1.Secret".
# This builds the actual expected shape instead.
json_escape() {
  local s="$1"
  s="${s//\\/\\\\}"
  s="${s//\"/\\\"}"
  printf '%s' "$s"
}

create_k8s_secret() {
  local name="$1" key="$2" value="$3"
  if sudo podman secret exists "$name" 2>/dev/null; then
    sudo podman secret rm "$name"
  fi
  printf '{"apiVersion":"v1","kind":"Secret","metadata":{"name":"%s"},"type":"Opaque","stringData":{"%s":"%s"}}' \
    "$(json_escape "$name")" "$(json_escape "$key")" "$(json_escape "$value")" \
    | sudo podman secret create "$name" -
}

# Self-locating paths — this script always operates on the repo it's part
# of, never on a separate hardcoded staging copy. Whatever directory this
# repo is checked out to (e.g. ~/ai/dow-k9-aif on one machine, ~/ai/das-dev
# on another), `build`/`secret`/`up`/`down` all follow it automatically.
# Set DAS_DEPLOY_DIR only to force a different parent dir (rare — e.g. a
# staging tree with its own k9-aif-framework checkout).
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DAS_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
REPO_ROOT="${DAS_DEPLOY_DIR:-$(cd "$DAS_DIR/.." && pwd)}"
DAS_DIRNAME="$(basename "$DAS_DIR")"
VOLUMES_DIR="${HOME}/containers/volumes/dow"
FRAMEWORK_REPO="https://github.com/k9aif/k9-aif-framework.git"
IMAGE="k9-aif-das:latest"
POD_NAME="k9-dow-pod"

cmd="${1:-help}"

case "$cmd" in

  clone)
    echo "Ensuring sibling repos are current in $REPO_ROOT ..."
    cd "$REPO_ROOT"

    if [[ -d "k9-aif-framework" ]]; then
      echo "  k9-aif-framework exists — pulling latest ..."
      git -C k9-aif-framework pull
    else
      git clone "$FRAMEWORK_REPO"
    fi

    echo "  $DAS_DIRNAME already present at $DAS_DIR — pulling latest ..."
    git -C "$DAS_DIR" pull

    # Create volume dirs (same pattern as EOC)
    mkdir -p "$VOLUMES_DIR"/{config,data,logs,runtime}
    echo ""
    echo "Clone/pull complete."
    echo "  $REPO_ROOT/k9-aif-framework/"
    echo "  $DAS_DIR/"
    echo "  $VOLUMES_DIR/ (config, data, logs, runtime)"
    ;;

  build)
    echo "Building $IMAGE from $REPO_ROOT (context dir: $DAS_DIRNAME) ..."
    cd "$REPO_ROOT"
    sudo podman build -t "$IMAGE" \
      -f "$DAS_DIRNAME/ubuntu/Containerfile" \
      .
    echo "Build complete: $IMAGE"
    ;;

  secret)
    ENV_FILE="$DAS_DIR/.env"
    [[ -f "$ENV_FILE" ]] || { echo "Error: $ENV_FILE not found."; exit 1; }

    # Neo4j password
    NEO4J_PW=$(grep -E '^NEO4J_PASSWORD=' "$ENV_FILE" | cut -d= -f2- | tr -d '[:space:]')
    create_k8s_secret neo4j-password neo4j-password "$NEO4J_PW"
    echo "Secret 'neo4j-password' stored."

    # Postgres password
    PG_PW=$(grep -E '^K9_PG_PASSWORD=' "$ENV_FILE" | cut -d= -f2- | tr -d '[:space:]')
    if [[ -n "$PG_PW" ]]; then
      create_k8s_secret pg-password pg-password "$PG_PW"
      echo "Secret 'pg-password' stored."
    else
      echo "Warning: K9_PG_PASSWORD not found in .env"
    fi

    # S3/MinIO access key + secret key
    S3_AKID=$(grep -E '^AWS_ACCESS_KEY_ID=' "$ENV_FILE" | cut -d= -f2- | tr -d '[:space:]')
    if [[ -n "$S3_AKID" ]]; then
      create_k8s_secret das-s3-access-key das-s3-access-key "$S3_AKID"
      echo "Secret 'das-s3-access-key' stored."
    else
      echo "Warning: AWS_ACCESS_KEY_ID not found in .env"
    fi

    S3_SECRET=$(grep -E '^AWS_SECRET_ACCESS_KEY=' "$ENV_FILE" | cut -d= -f2- | tr -d '[:space:]')
    if [[ -n "$S3_SECRET" ]]; then
      create_k8s_secret das-s3-secret-key das-s3-secret-key "$S3_SECRET"
      echo "Secret 'das-s3-secret-key' stored."
    else
      echo "Warning: AWS_SECRET_ACCESS_KEY not found in .env"
    fi
    ;;

  up)
    echo "Deploying pod: $POD_NAME (3 containers) ..."
    sudo podman play kube "$DAS_DIR/ubuntu/das-pod.yaml" --replace
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
    ENV_FILE="$DAS_DIR/.env"
    [[ -f "$ENV_FILE" ]] || { echo "Error: $ENV_FILE not found."; exit 1; }
    PODMAN_HOST_IP="${PODMAN_HOST_IP:-$(hostname -I | awk '{print $1}')}"
    echo "Starting DAS in demo mode (app-backend only, no router/orchestrator) ..."
    sudo podman run -d --rm \
      --name das-demo \
      -p 8000:8000 \
      --add-host "rhel-host:${PODMAN_HOST_IP}" \
      --env-file "$ENV_FILE" \
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
    sudo podman play kube "$DAS_DIR/ubuntu/das-pod.yaml" --down || true
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
