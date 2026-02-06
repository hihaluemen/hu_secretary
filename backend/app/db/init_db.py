import pymysql

from app.core.config import get_settings


def init_mysql_db() -> None:
    settings = get_settings()
    conn = pymysql.connect(
        host=settings.MYSQL_HOST,
        port=settings.MYSQL_PORT,
        user=settings.MYSQL_USER,
        password=settings.MYSQL_PASSWORD,
        charset=settings.MYSQL_CHARSET,
    )
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS {settings.MYSQL_DB} DEFAULT CHARACTER SET utf8mb4"
            )
            conn.select_db(settings.MYSQL_DB)
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS events (
                    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '事件ID',
                    user_id VARCHAR(50) NOT NULL COMMENT '用户ID',
                    event VARCHAR(255) NOT NULL COMMENT '事件核心内容',
                    event_time DATETIME NOT NULL COMMENT '开始时间（标准格式：YYYY-MM-DD HH:MM:SS）',
                    location VARCHAR(255) NOT NULL COMMENT '事件地点',
                    participants VARCHAR(500) NOT NULL COMMENT '参与人员（原始表述）',
                    remark VARCHAR(500) NULL COMMENT '事件提醒信息',
                    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
                    INDEX idx_user_time (user_id, event_time),
                    INDEX idx_event (event(191)),
                    INDEX idx_location (location(191))
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='日常事件表（仅保留开始时间）'
                """
            )
        conn.commit()
    finally:
        conn.close()

