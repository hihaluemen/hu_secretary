from app.services.assistant_service import AssistantService


class DummyLLMService:
    def __init__(self, responses: list[str]) -> None:
        self.responses = responses

    def chat(self, messages: list[dict], temperature: float = 0.0, seed: int | None = 12345) -> str:
        if self.responses:
            return self.responses.pop(0)
        return ""


class DummyEventRepository:
    def list_events(self, user_id: str) -> list[dict]:
        return []


def _build_service(responses: list[str] | None = None) -> AssistantService:
    return AssistantService(
        llm_service=DummyLLMService(responses or []),
        event_repository=DummyEventRepository(),
    )


def test_parse_json_payload_supports_wrapped_text_and_fenced_json():
    service = _build_service()
    payload = """
解析结果如下：
```json
[{"content":"明天下午开会","flag":2,"type":"新增"}]
```
请以此为准。
"""
    data = service._parse_json_payload(payload)
    assert isinstance(data, list)
    assert data[0]["flag"] == 2


def test_replace_midnight_defaults_uses_reasonable_time_buckets():
    service = _build_service()
    assert service._replace_midnight_defaults("2026-02-10 00:00", "大后天上午开会") == "2026-02-10 10:00"
    assert service._replace_midnight_defaults("2026-02-10 00:00", "大后天下午开会") == "2026-02-10 16:00"
    assert service._replace_midnight_defaults("2026-02-10 00:00", "大后天晚上开会") == "2026-02-10 20:00"
    assert service._replace_midnight_defaults("2026-02-10 00:00", "大后天开会") == "2026-02-10 09:00"


def test_replace_midnight_defaults_supports_t_separator_and_seconds():
    service = _build_service()
    normalized = "安排在 2026-02-10T00:00:00 和你讨论"
    output = service._replace_midnight_defaults(normalized, "大后天晚上讨论")
    assert "2026-02-10T20:00" in output


def test_extract_events_returns_empty_list_on_invalid_json_response():
    service = _build_service(["这个请求无法提取为 JSON"])
    result = service.extract_events("明天下午跟张总开会")
    assert result == []

