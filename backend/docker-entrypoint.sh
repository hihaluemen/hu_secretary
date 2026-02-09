#!/usr/bin/env sh
set -eu

echo "[backend] waiting for MySQL ${MYSQL_HOST:-mysql}:${MYSQL_PORT:-3306} ..."
python - <<'PY'
import os
import time

import pymysql


host = os.getenv("MYSQL_HOST", "mysql")
port = int(os.getenv("MYSQL_PORT", "3306"))
user = os.getenv("MYSQL_USER", "root")
password = os.getenv("MYSQL_PASSWORD", "")
charset = os.getenv("MYSQL_CHARSET", "utf8mb4")
timeout_seconds = int(os.getenv("MYSQL_WAIT_TIMEOUT", "60"))
deadline = time.time() + timeout_seconds

last_error = None
while time.time() < deadline:
    try:
        conn = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            charset=charset,
            connect_timeout=3,
            read_timeout=3,
            write_timeout=3,
        )
        conn.close()
        print("[backend] MySQL is ready")
        break
    except Exception as exc:  # noqa: BLE001
        last_error = str(exc)
        time.sleep(1)
else:
    raise SystemExit(f"[backend] MySQL not ready in {timeout_seconds}s: {last_error}")
PY

echo "[backend] init database schema ..."
python scripts/init_db.py

echo "[backend] start uvicorn ..."
exec python -m uvicorn app.main:app --host 0.0.0.0 --port "${APP_PORT:-8000}"
