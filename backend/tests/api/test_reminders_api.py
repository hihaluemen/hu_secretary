from datetime import datetime

from fastapi.testclient import TestClient

from app.main import app
from app.services.reminder_service import ReminderService

client = TestClient(app)


def test_reminders_tomorrow_api(monkeypatch):
    def fake_list(self, user_id: str, now: datetime | None = None):
        return {
            "user_id": user_id,
            "remind_date": "2026-02-09",
            "target_date": "2026-02-10",
            "total": 1,
            "items": [
                {
                    "event_id": 1,
                    "user_id": user_id,
                    "event": "项目会议",
                    "event_time": "2026-02-10 09:00:00",
                    "location": "A会议室",
                    "participants": "李总",
                    "remark": "带资料",
                    "remind_date": "2026-02-09",
                    "target_date": "2026-02-10",
                }
            ],
        }

    monkeypatch.setattr(ReminderService, "list_tomorrow_reminders", fake_list)
    response = client.get("/api/v1/reminders/tomorrow", params={"user_id": "user_001"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 1
    assert payload["items"][0]["event"] == "项目会议"
