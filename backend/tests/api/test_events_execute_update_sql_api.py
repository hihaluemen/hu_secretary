from fastapi.testclient import TestClient

from app.api.v1 import events as events_api
from app.main import app
from app.repositories.event_repository import EventRepository


client = TestClient(app)


class _DummySettings:
    def __init__(self, update_enabled: bool) -> None:
        self.DEMO_ENABLE_UPDATE_EXECUTE = update_enabled
        self.DEMO_ENABLE_RESET = True


def test_execute_update_sql_rejected_when_feature_disabled(monkeypatch):
    monkeypatch.setattr(events_api, "get_settings", lambda: _DummySettings(update_enabled=False))

    response = client.post(
        "/api/v1/events/execute-update-sql",
        json={
            "user_id": "user_001",
            "sql": "UPDATE events SET location = 'A会议室' WHERE id = 1",
        },
    )

    assert response.status_code == 400
    payload = response.json()
    assert payload["code"] == "DEMO_UPDATE_EXECUTE_DISABLED"


def test_execute_update_sql_success(monkeypatch):
    monkeypatch.setattr(events_api, "get_settings", lambda: _DummySettings(update_enabled=True))

    def fake_execute_update_sql(self, user_id: str, sql: str) -> int:
        assert user_id == "user_001"
        assert "UPDATE events" in sql
        return 2

    monkeypatch.setattr(EventRepository, "execute_update_sql", fake_execute_update_sql)

    response = client.post(
        "/api/v1/events/execute-update-sql",
        json={
            "user_id": "user_001",
            "sql": "UPDATE events SET location = 'A会议室' WHERE id = 1",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "success"
    assert payload["affected_rows"] == 2


def test_batch_create_events_success(monkeypatch):
    def fake_insert_events(self, user_id: str, events: list[dict]):
        assert user_id == "user_001"
        assert len(events) == 1
        return {
            "status": "success",
            "msg": "✅ 成功写入1条，❌ 失败0条",
            "detail": ["事件[项目会议]：写入成功（2026-02-15 09:00:00）"],
            "success_count": 1,
            "fail_count": 0,
        }

    monkeypatch.setattr(EventRepository, "insert_events", fake_insert_events)

    response = client.post(
        "/api/v1/events/batch-create",
        json={
            "user_id": "user_001",
            "events": [
                {
                    "event": "项目会议",
                    "event_time": "2026-02-15 09:00:00",
                    "location": "A会议室",
                    "participants": "李总",
                    "remark": "带资料",
                }
            ],
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "success"
    assert payload["success_count"] == 1
