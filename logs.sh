#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

if ! command -v docker >/dev/null 2>&1; then
  echo "[logs] docker 未安装。"
  exit 1
fi

if ! docker compose version >/dev/null 2>&1; then
  echo "[logs] docker compose 不可用。"
  exit 1
fi

SERVICE="${SERVICE:-all}"
FOLLOW="${FOLLOW:-true}"
TAIL="${TAIL:-200}"
SINCE="${SINCE:-}"

compose_args=(logs)

if [ "$FOLLOW" = "true" ]; then
  compose_args+=(-f)
fi

if [ -n "$TAIL" ]; then
  compose_args+=("--tail=$TAIL")
fi

if [ -n "$SINCE" ]; then
  compose_args+=("--since=$SINCE")
fi

case "$SERVICE" in
  all)
    ;;
  backend|frontend|mysql)
    compose_args+=("$SERVICE")
    ;;
  *)
    echo "[logs] SERVICE 仅支持: all|backend|frontend|mysql"
    echo "[logs] 示例: SERVICE=backend FOLLOW=true TAIL=300 ./logs.sh"
    exit 1
    ;;
esac

echo "[logs] SERVICE=$SERVICE FOLLOW=$FOLLOW TAIL=${TAIL:-<none>} SINCE=${SINCE:-<none>}"
docker compose "${compose_args[@]}"
