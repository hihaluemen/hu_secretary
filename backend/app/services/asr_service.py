import base64
import time

from app.core.config import get_settings
from app.core.exceptions import BadRequestError


class ASRService:
    def __init__(self) -> None:
        self._settings = get_settings()

    def _build_data_uri(self, audio_bytes: bytes, mime_type: str) -> str:
        base64_str = base64.b64encode(audio_bytes).decode()
        return f"data:{mime_type};base64,{base64_str}"

    def transcribe(self, audio_bytes: bytes, mime_type: str) -> dict[str, str | int]:
        try:
            import dashscope
        except Exception as exc:  # noqa: BLE001
            raise BadRequestError(message="未安装 dashscope 依赖", code="ASR_DEPENDENCY_MISSING") from exc

        if self._settings.ASR_PROVIDER != "dashscope":
            raise BadRequestError(message="当前仅支持 dashscope ASR", code="ASR_PROVIDER_UNSUPPORTED")

        if not self._settings.DASHSCOPE_API_KEY:
            raise BadRequestError(message="缺少 DASHSCOPE_API_KEY", code="ASR_API_KEY_MISSING")

        dashscope.base_http_api_url = self._settings.DASHSCOPE_BASE_URL
        data_uri = self._build_data_uri(audio_bytes, mime_type)
        messages = [
            {"role": "system", "content": [{"text": ""}]},
            {"role": "user", "content": [{"audio": data_uri}]},
        ]

        started_at = time.time()
        try:
            response = dashscope.MultiModalConversation.call(
                api_key=self._settings.DASHSCOPE_API_KEY,
                model=self._settings.DASHSCOPE_ASR_MODEL,
                messages=messages,
                result_format="message",
                asr_options={"enable_itn": False},
            )
        except Exception as exc:  # noqa: BLE001
            raise BadRequestError(message=f"ASR 调用失败: {exc}", code="ASR_CALL_FAILED") from exc
        duration_ms = int((time.time() - started_at) * 1000)

        text = self._extract_text(response)
        if not text:
            raise BadRequestError(message="ASR 未返回可用文本", code="ASR_EMPTY_RESULT")

        return {
            "text": text,
            "provider": "dashscope",
            "model": self._settings.DASHSCOPE_ASR_MODEL,
            "duration_ms": duration_ms,
        }

    def _extract_text(self, response: object) -> str:
        output = getattr(response, "output", None)
        if output is None and isinstance(response, dict):
            output = response.get("output")

        if not output:
            return ""

        choices = None
        if isinstance(output, dict):
            choices = output.get("choices")
        elif hasattr(output, "choices"):
            choices = getattr(output, "choices")
        if not choices:
            return ""

        first_choice = choices[0] if choices else {}
        message = {}
        if isinstance(first_choice, dict):
            message = first_choice.get("message", {})
        elif hasattr(first_choice, "message"):
            message = getattr(first_choice, "message")

        content = []
        if isinstance(message, dict):
            content = message.get("content", [])
        elif hasattr(message, "content"):
            content = getattr(message, "content")

        texts: list[str] = []
        for item in content:
            text = None
            if isinstance(item, dict):
                text = item.get("text")
            elif hasattr(item, "text"):
                text = getattr(item, "text")
            if isinstance(text, str) and text.strip():
                texts.append(text.strip())

        if texts:
            return "\n".join(texts)

        text = None
        if isinstance(output, dict):
            text = output.get("text")
        elif hasattr(output, "text"):
            text = getattr(output, "text")
        if isinstance(text, str):
            return text.strip()

        return ""
