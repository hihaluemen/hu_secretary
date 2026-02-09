#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

if ! command -v docker >/dev/null 2>&1; then
  echo "[cleanup] docker 未安装。"
  exit 1
fi

if ! docker compose version >/dev/null 2>&1; then
  echo "[cleanup] docker compose 不可用。"
  exit 1
fi

REMOVE_IMAGES="${REMOVE_IMAGES:-false}"
REMOVE_VOLUMES="${REMOVE_VOLUMES:-false}"

echo "[cleanup] 停止并移除容器..."
DOWN_ARGS=""
if [ "${REMOVE_VOLUMES}" = "true" ]; then
  DOWN_ARGS="-v"
fi

docker compose down ${DOWN_ARGS}

if [ "${REMOVE_IMAGES}" = "true" ]; then
  echo "[cleanup] 移除本项目镜像..."
  docker image rm -f mishu-backend:local mishu-frontend:local 2>/dev/null || true
fi

echo "[cleanup] 完成。REMOVE_IMAGES=${REMOVE_IMAGES}, REMOVE_VOLUMES=${REMOVE_VOLUMES}"
