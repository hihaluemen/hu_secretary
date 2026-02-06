from typing import Any

import pymysql

from app.core.exceptions import NotFoundError
from app.db.mysql import mysql_conn_context


class EventRepository:
    def _normalize_event_payload(self, payload: dict[str, Any]) -> dict[str, Any]:
        event_content = str(payload.get("事件内容") or payload.get("event") or "未知活动").strip()
        event_time = str(payload.get("开始时间") or payload.get("event_time") or "").strip()
        if len(event_time) == 16:
            event_time = f"{event_time}:00"
        location = str(payload.get("地点") or payload.get("location") or "地点未确定").strip()
        participants = str(payload.get("人物") or payload.get("participants") or "未知人员").strip() or "未知人员"
        remark = str(payload.get("remark") or "").strip()
        return {
            "event": event_content,
            "event_time": event_time,
            "location": location,
            "participants": participants,
            "remark": remark,
        }

    def insert_events(self, user_id: str, events: list[dict[str, Any]]) -> dict[str, Any]:
        success_count = 0
        fail_count = 0
        detail: list[str] = []

        with mysql_conn_context() as conn:
            with conn.cursor() as cursor:
                for event in events:
                    normalized = self._normalize_event_payload(event)
                    event_content = normalized["event"]
                    event_time = normalized["event_time"]
                    location = normalized["location"]
                    participants = normalized["participants"]
                    remark = normalized["remark"]

                    cursor.execute(
                        """
                        SELECT id FROM events
                        WHERE user_id = %s AND event = %s AND event_time = %s
                        LIMIT 1
                        """,
                        (user_id, event_content, event_time),
                    )
                    if cursor.fetchone():
                        fail_count += 1
                        detail.append(f"事件[{event_content}]：重复事件（{event_time}）")
                        continue

                    cursor.execute(
                        """
                        INSERT INTO events (user_id, event, event_time, location, participants, remark)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        """,
                        (user_id, event_content, event_time, location, participants, remark),
                    )
                    success_count += 1
                    detail.append(f"事件[{event_content}]：写入成功（{event_time}）")

            conn.commit()

        return {
            "status": "success" if success_count > 0 else "failed",
            "msg": f"✅ 成功写入{success_count}条，❌ 失败{fail_count}条",
            "detail": detail,
            "success_count": success_count,
            "fail_count": fail_count,
        }

    def list_events(
        self,
        user_id: str,
        keyword: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> list[dict[str, Any]]:
        conditions = ["user_id = %s"]
        params: list[Any] = [user_id]

        if keyword:
            conditions.append("(event LIKE %s OR location LIKE %s OR participants LIKE %s OR remark LIKE %s)")
            keyword_like = f"%{keyword}%"
            params.extend([keyword_like, keyword_like, keyword_like, keyword_like])

        if date_from:
            conditions.append("event_time >= %s")
            params.append(f"{date_from} 00:00:00")

        if date_to:
            conditions.append("event_time <= %s")
            params.append(f"{date_to} 23:59:59")

        where_sql = " AND ".join(conditions)
        with mysql_conn_context() as conn:
            with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute(
                    f"""
                    SELECT id, user_id, event, event_time, location, participants, remark, create_time, update_time
                    FROM events
                    WHERE {where_sql}
                    ORDER BY event_time ASC
                    """,
                    tuple(params),
                )
                return cursor.fetchall()

    def get_event(self, event_id: int, user_id: str) -> dict[str, Any]:
        with mysql_conn_context() as conn:
            with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute(
                    """
                    SELECT id, user_id, event, event_time, location, participants, remark, create_time, update_time
                    FROM events
                    WHERE id = %s AND user_id = %s
                    LIMIT 1
                    """,
                    (event_id, user_id),
                )
                row = cursor.fetchone()
                if not row:
                    raise NotFoundError(message=f"事件不存在: id={event_id}", code="EVENT_NOT_FOUND")
                return row

    def create_event(self, user_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        normalized = self._normalize_event_payload(payload)
        with mysql_conn_context() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO events (user_id, event, event_time, location, participants, remark)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (
                        user_id,
                        normalized["event"],
                        normalized["event_time"],
                        normalized["location"],
                        normalized["participants"],
                        normalized["remark"],
                    ),
                )
                event_id = cursor.lastrowid
            conn.commit()
        return self.get_event(event_id, user_id)

    def update_event(self, event_id: int, user_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        original = self.get_event(event_id, user_id)
        normalized = {
            "event": payload.get("event", original["event"]),
            "event_time": payload.get("event_time", original["event_time"]),
            "location": payload.get("location", original["location"]),
            "participants": payload.get("participants", original["participants"]),
            "remark": payload.get("remark", original["remark"]),
        }
        if isinstance(normalized["event_time"], str) and len(normalized["event_time"].strip()) == 16:
            normalized["event_time"] = f"{normalized['event_time']}:00"

        with mysql_conn_context() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE events
                    SET event = %s,
                        event_time = %s,
                        location = %s,
                        participants = %s,
                        remark = %s,
                        update_time = NOW()
                    WHERE id = %s AND user_id = %s
                    """,
                    (
                        normalized["event"],
                        normalized["event_time"],
                        normalized["location"],
                        normalized["participants"],
                        normalized["remark"],
                        event_id,
                        user_id,
                    ),
                )
            conn.commit()
        return self.get_event(event_id, user_id)

    def delete_event(self, event_id: int, user_id: str) -> None:
        with mysql_conn_context() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    DELETE FROM events
                    WHERE id = %s AND user_id = %s
                    """,
                    (event_id, user_id),
                )
                if cursor.rowcount == 0:
                    raise NotFoundError(message=f"事件不存在: id={event_id}", code="EVENT_NOT_FOUND")
            conn.commit()

    def clear_events(self, user_id: str) -> int:
        with mysql_conn_context() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    DELETE FROM events WHERE user_id = %s
                    """,
                    (user_id,),
                )
                affected = cursor.rowcount
            conn.commit()
            return affected
