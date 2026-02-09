from app.core.exceptions import BadRequestError
from app.services.asr_service import ASRService


def test_extract_text_from_dict_response():
    service = ASRService()
    response = {
        "output": {
            "choices": [
                {
                    "message": {
                        "content": [
                            {"text": "你好"},
                            {"text": "世界"},
                        ]
                    }
                }
            ]
        }
    }
    assert service._extract_text(response) == "你好\n世界"


def test_transcribe_raises_when_api_key_missing(monkeypatch):
    monkeypatch.setenv("DASHSCOPE_API_KEY", "")
    service = ASRService()
    service._settings.DASHSCOPE_API_KEY = ""
    try:
        service.transcribe(audio_bytes=b"abc", mime_type="audio/webm")
    except BadRequestError as exc:
        assert exc.code in {"ASR_API_KEY_MISSING", "ASR_DEPENDENCY_MISSING"}
    else:
        raise AssertionError("expected BadRequestError")
