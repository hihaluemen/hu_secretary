from pathlib import Path
import sys


BACKEND_ROOT = Path(__file__).resolve().parents[1]

if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.db.init_db import init_mysql_db


if __name__ == "__main__":
    init_mysql_db()
    print("✅ MySQL 初始化完成")
