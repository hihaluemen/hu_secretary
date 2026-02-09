#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

if ! command -v docker >/dev/null 2>&1; then
  echo "[deploy] docker 未安装，请先安装 Docker。"
  exit 1
fi

if ! docker compose version >/dev/null 2>&1; then
  echo "[deploy] docker compose 不可用，请升级 Docker 或安装 compose 插件。"
  exit 1
fi

if [ ! -f ".env" ]; then
  if [ -f ".env.example" ]; then
    cp .env.example .env
    echo "[deploy] 已从 .env.example 创建 .env，请补充密钥配置后重试。"
  else
    echo "[deploy] 缺少 .env，请先创建。"
  fi
  exit 1
fi

export DOCKER_REGISTRY="${DOCKER_REGISTRY:-}"
export USE_CN_MIRROR="${USE_CN_MIRROR:-false}"
export USE_DOCKER_MYSQL="${USE_DOCKER_MYSQL:-false}"
export HTTP_PORT="${HTTP_PORT:-8655}"
export HTTPS_PORT="${HTTPS_PORT:-8656}"
mysql_host_from_env="$(awk -F= '/^MYSQL_HOST=/{sub(/^MYSQL_HOST=/,""); print $0}' .env | tail -n 1)"
mysql_port_from_env="$(awk -F= '/^MYSQL_PORT=/{sub(/^MYSQL_PORT=/,""); print $0}' .env | tail -n 1)"
mysql_user_from_env="$(awk -F= '/^MYSQL_USER=/{sub(/^MYSQL_USER=/,""); print $0}' .env | tail -n 1)"
mysql_password_from_env="$(awk -F= '/^MYSQL_PASSWORD=/{sub(/^MYSQL_PASSWORD=/,""); print $0}' .env | tail -n 1)"
mysql_db_from_env="$(awk -F= '/^MYSQL_DB=/{sub(/^MYSQL_DB=/,""); print $0}' .env | tail -n 1)"

export MYSQL_HOST="${MYSQL_HOST:-${mysql_host_from_env:-host.docker.internal}}"
export MYSQL_PORT="${MYSQL_PORT:-${mysql_port_from_env:-3306}}"
export MYSQL_USER="${MYSQL_USER:-${mysql_user_from_env:-root}}"

export MYSQL_PASSWORD="${MYSQL_PASSWORD:-$mysql_password_from_env}"
export MYSQL_DB="${MYSQL_DB:-${mysql_db_from_env:-daily_assistant}}"

if [ -n "$DOCKER_REGISTRY" ] && [ "${DOCKER_REGISTRY%/}" = "$DOCKER_REGISTRY" ]; then
  export DOCKER_REGISTRY="${DOCKER_REGISTRY}/"
fi

if [ "$USE_DOCKER_MYSQL" = "true" ]; then
  export MYSQL_HOST="mysql"
  export MYSQL_PORT="3306"
  export MYSQL_USER="root"
  export MYSQL_ROOT_PASSWORD="${MYSQL_ROOT_PASSWORD:-${MYSQL_PASSWORD:-$mysql_password_from_env}}"
  export MYSQL_PASSWORD="${MYSQL_ROOT_PASSWORD}"

  if [ -z "${MYSQL_ROOT_PASSWORD:-}" ]; then
    echo "[deploy] USE_DOCKER_MYSQL=true 时，需要设置 MYSQL_ROOT_PASSWORD（或 .env 里 MYSQL_PASSWORD）。"
    exit 1
  fi
else
  if [ -z "${MYSQL_PASSWORD:-}" ]; then
    echo "[deploy] USE_DOCKER_MYSQL=false 时，需要设置外部数据库密码 MYSQL_PASSWORD（或 .env 里 MYSQL_PASSWORD）。"
    exit 1
  fi
fi

echo "[deploy] 参数："
echo "  DOCKER_REGISTRY=${DOCKER_REGISTRY:-<官方源>}"
echo "  USE_CN_MIRROR=${USE_CN_MIRROR}"
echo "  USE_DOCKER_MYSQL=${USE_DOCKER_MYSQL}"
echo "  HTTP_PORT=${HTTP_PORT} HTTPS_PORT=${HTTPS_PORT}"
echo "  MYSQL_HOST=${MYSQL_HOST} MYSQL_PORT=${MYSQL_PORT} MYSQL_DB=${MYSQL_DB} MYSQL_USER=${MYSQL_USER}"

if [ "${DOCKER_LOGIN:-false}" = "true" ]; then
  if [ -z "${DOCKER_LOGIN_REGISTRY:-}" ] || [ -z "${DOCKER_LOGIN_USERNAME:-}" ] || [ -z "${DOCKER_LOGIN_PASSWORD:-}" ]; then
    echo "[deploy] DOCKER_LOGIN=true 时，需要同时设置 DOCKER_LOGIN_REGISTRY/DOCKER_LOGIN_USERNAME/DOCKER_LOGIN_PASSWORD"
    exit 1
  fi
  echo "[deploy] 执行 docker login ${DOCKER_LOGIN_REGISTRY}"
  docker login "${DOCKER_LOGIN_REGISTRY}" -u "${DOCKER_LOGIN_USERNAME}" -p "${DOCKER_LOGIN_PASSWORD}"
fi

echo "[deploy] 开始构建并启动..."
if [ "$USE_DOCKER_MYSQL" = "true" ]; then
  docker compose --profile with-mysql up -d --build
else
  docker compose up -d --build backend frontend
fi

echo "[deploy] 启动完成："
echo "  前端 HTTP:  http://localhost:${HTTP_PORT}"
echo "  前端 HTTPS: https://localhost:${HTTPS_PORT}"
echo "  API 入口:   http://localhost:${HTTP_PORT}/api/v1/health"
