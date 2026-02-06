#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "[INFO] E2E smoke start"

cd "$ROOT_DIR"

if [ ! -d "backend/.venv" ]; then
  echo "[ERROR] backend/.venv 不存在，请先创建并安装依赖"
  exit 1
fi

if [ ! -d "frontend/node_modules" ]; then
  echo "[ERROR] frontend/node_modules 不存在，请先 npm install"
  exit 1
fi

echo "[INFO] 校验后端导入"
(cd backend && source .venv/bin/activate && python -c "from app.main import app; print('backend import ok')")

echo "[INFO] 校验前端构建"
(cd frontend && npm run build >/tmp/mishu_frontend_build.log)

echo "[INFO] E2E smoke done"
echo "[INFO] 后续可扩展: 启动服务后调用 /api/v1/assistant/process 完整链路验证"
