#!/usr/bin/env bash
# K9-AIF DAS — Podman build and deploy helper
# Run from any directory on the Podman host (no sudo needed — script handles it).
#
# Commands:
#   clone        — pull latest on this repo
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
# repo is checked out to (e.g. ~/ai/dow-k9-aif on one machine, ~/ai/dow-k9x
# on another), `build`/`secret`/`up`/`down` all follow it automatically.
# Set DAS_DEPLOY_DIR only to force a different parent dir for the build
# context (rare).
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DAS_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
REPO_ROOT="${DAS_DEPLOY_DIR:-$(cd "$DAS_DIR/.." && pwd)}"
DAS_DIRNAME="$(basename "$DAS_DIR")"
VOLUMES_DIR="${HOME}/containers/volumes/dow"
IMAGE="k9-aif-das:latest"
POD_NAME="k9-dow-pod"

cmd="${1:-help}"

case "$cmd" in

  clone)
    # DAS consumes the framework as the k9-aif[s3] PyPI package (see
    # requirements.txt) — no sibling k9-aif-framework checkout needed for
    # the build. This just pulls latest on the repo itself.
    echo "Pulling latest for $DAS_DIRNAME at $DAS_DIR ..."
    git -C "$DAS_DIR" pull

    # Create volume dirs (same pattern as EOC)
    mkdir -p "$VOLUMES_DIR"/{config,data,logs,runtime}
    echo ""
    echo "Pull complete."
    echo "  $DAS_DIR/"
    echo "  $VOLUMES_DIR/ (config, data, logs, runtime)"
    ;;

  build)
    # --no-cache: requirements.txt pins k9-aif[s3] with a floor (>=1.4.0),
    # not an exact version — an unchanged requirements.txt hashes to the
    # same cached pip-install layer, so Podman would silently keep
    # whatever PyPI release was current the *first* time this built,
    # even after a newer release ships real fixes (bit us for real: the
    # 1.10.5 llm_invoke retry fix never reached a running container until
    # a forced rebuild). Slower every time, but correctness > speed here.
    echo "Building $IMAGE from $REPO_ROOT (context dir: $DAS_DIRNAME, no cache) ..."
    cd "$REPO_ROOT"
    sudo podman build --no-cache -t "$IMAGE" \
      -f "$DAS_DIRNAME/ubuntu/Containerfile" \
      --build-arg "DAS_SRC_DIR=$DAS_DIRNAME" \
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
    # <PODMAN_HOST_IP> is substituted into a throwaway rendered copy on
    # every deploy, never into the tracked das-pod.yaml — a one-time
    # manual `sed` on the tracked file is an uncommitted local edit that
    # a fresh clone/pull/reset can silently wipe out (this bit us
    # repeatedly). PODMAN_HOST_IP env var overrides auto-detection.
    PODMAN_HOST_IP="${PODMAN_HOST_IP:-$(hostname -I | awk '{print $1}')}"
    RENDERED_YAML="$(mktemp /tmp/das-pod.XXXXXX.yaml)"
    trap 'rm -f "$RENDERED_YAML"' EXIT
    sed "s/<PODMAN_HOST_IP>/${PODMAN_HOST_IP}/g" "$DAS_DIR/ubuntu/das-pod.yaml" > "$RENDERED_YAML"
    echo "Deploying pod: $POD_NAME (3 containers, host IP ${PODMAN_HOST_IP}) ..."
    sudo podman play kube "$RENDERED_YAML" --replace
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
    echo "  clone        — pull latest on this repo"
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
