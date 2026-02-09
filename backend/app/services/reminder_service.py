from datetime import datetime, timedelta

from app.core.config import get_settings
from app.repositories.event_repository import EventRepository


class ReminderService:
    def __init__(self, event_repository: EventRepository | None = None) -> None:
        self._settings = get_settings()
        self._event_repository = event_repository or EventRepository()

    def _resolve_now(self, now: datetime | None = None) -> datetime:
        if now is not None:
            if now.tzinfo is None:
                return now.replace(tzinfo=self._settings.reminder_timezone)
            return now.astimezone(self._settings.reminder_timezone)
        return datetime.now(self._settings.reminder_timezone)

    def list_tomorrow_reminders(self, user_id: str, now: datetime | None = None) -> dict:
        reference = self._resolve_now(now)
        target_date = (reference + timedelta(days=max(self._settings.REMINDER_SCAN_DAYS_AHEAD, 1))).date()
        target_date_str = target_date.strftime("%Y-%m-%d")
        remind_date_str = reference.date().strftime("%Y-%m-%d")

        rows = self._event_repository.list_events(
            user_id=user_id,
            date_from=target_date_str,
            date_to=target_date_str,
        )

        items = [
            {
                "event_id": row["id"],
                "user_id": row["user_id"],
                "event": row["event"],
                "event_time": row["event_time"],
                "location": row["location"],
                "participants": row["participants"],
                "remark": row.get("remark"),
                "remind_date": remind_date_str,
                "target_date": target_date_str,
            }
            for row in rows
        ]

        return {
            "user_id": user_id,
            "remind_date": remind_date_str,
            "target_date": target_date_str,
            "total": len(items),
            "items": items,
        }
