from io import BytesIO

from fastapi.testclient import TestClient

from app.main import app
from app.services.asr_service import ASRService

client = TestClient(app)


def test_asr_transcribe_rejects_unsupported_mime():
    files = {"file": ("demo.txt", BytesIO(b"hello"), "text/plain")}
    response = client.post("/api/v1/asr/transcribe", files=files, data={"user_id": "user_001"})
    assert response.status_code == 400
    payload = response.json()
    assert payload["code"] == "ASR_UNSUPPORTED_MIME"


def test_asr_transcribe_requires_file():
    response = client.post("/api/v1/asr/transcribe", data={"user_id": "user_001"})
    assert response.status_code == 422


def test_asr_transcribe_accepts_mime_with_codecs(monkeypatch):
    def fake_transcribe(self, audio_bytes: bytes, mime_type: str):
        return {
            "text": "测试转写",
            "provider": "dashscope",
            "model": "qwen3-asr-flash",
            "duration_ms": 10,
        }

    monkeypatch.setattr(ASRService, "transcribe", fake_transcribe)
    files = {"file": ("demo.webm", BytesIO(b"audio-bytes"), "audio/webm;codecs=opus")}
    response = client.post("/api/v1/asr/transcribe", files=files, data={"user_id": "user_001"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["text"] == "测试转写"
