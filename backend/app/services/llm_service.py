from openai import BadRequestError as OpenAIBadRequestError
from openai import OpenAI

from app.core.config import get_settings


class LLMService:
    def __init__(self) -> None:
        settings = get_settings()
        self._settings = settings
        self._client = OpenAI(
            api_key=settings.llm_api_key,
            base_url=settings.llm_base_url,
            timeout=settings.LLM_TIMEOUT_SECONDS,
        )

    def chat(self, messages: list[dict], temperature: float = 0.0, seed: int | None = 12345) -> str:
        resolved_temperature = temperature
        if self._settings.llm_provider == "kimi":
            resolved_temperature = 1

        try:
            response = self._client.chat.completions.create(
                model=self._settings.llm_model,
                messages=messages,
                temperature=resolved_temperature,
                seed=seed,
            )
        except OpenAIBadRequestError as exc:
            error_text = str(exc)
            if "invalid temperature" in error_text and "only 1 is allowed" in error_text:
                response = self._client.chat.completions.create(
                    model=self._settings.llm_model,
                    messages=messages,
                    temperature=1,
                    seed=seed,
                )
            else:
                raise

        return (response.choices[0].message.content or "").strip()
