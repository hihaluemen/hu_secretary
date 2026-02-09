from datetime import datetime

from app.services.reminder_service import ReminderService


class DummyEventRepository:
    def __init__(self, rows: list[dict] | None = None) -> None:
        self.rows = rows or []
        self.last_call = {}

    def list_events(self, user_id: str, keyword=None, date_from=None, date_to=None):
        self.last_call = {
            "user_id": user_id,
            "date_from": date_from,
            "date_to": date_to,
        }
        return self.rows


def test_list_tomorrow_reminders_filters_by_next_day():
    repo = DummyEventRepository(
        rows=[
            {
                "id": 1,
                "user_id": "user_001",
                "event": "项目评审",
                "event_time": "2026-02-10 09:00:00",
                "location": "A会议室",
                "participants": "李总",
                "remark": "带资料",
            }
        ]
    )
    service = ReminderService(event_repository=repo)
    result = service.list_tomorrow_reminders(
        user_id="user_001",
        now=datetime.fromisoformat("2026-02-09T08:00:00+08:00"),
    )
    assert result["target_date"] == "2026-02-10"
    assert result["remind_date"] == "2026-02-09"
    assert result["total"] == 1
    assert repo.last_call["date_from"] == "2026-02-10"
    assert repo.last_call["date_to"] == "2026-02-10"


def test_list_tomorrow_reminders_empty_result():
    repo = DummyEventRepository(rows=[])
    service = ReminderService(event_repository=repo)
    result = service.list_tomorrow_reminders(
        user_id="user_001",
        now=datetime.fromisoformat("2026-02-09T08:00:00+08:00"),
    )
    assert result["total"] == 0
    assert result["items"] == []
