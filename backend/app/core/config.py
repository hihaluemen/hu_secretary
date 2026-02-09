from functools import lru_cache
from zoneinfo import ZoneInfo

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_NAME: str = "mishu-demo"
    APP_ENV: str = "dev"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    API_PREFIX: str = "/api/v1"
    CORS_ORIGINS: str = "http://localhost:5173"

    LLM_PROVIDER: str = "kimi"
    LLM_TIMEOUT_SECONDS: int = 30

    KIMI_API_KEY: str = ""
    KIMI_BASE_URL: str = "https://api.moonshot.cn/v1"
    KIMI_MODEL: str = "kimi-k2-turbo-preview"

    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    OPENAI_MODEL: str = "gpt-4o-mini"

    ASR_PROVIDER: str = "dashscope"
    ASR_TIMEOUT_SECONDS: int = 60
    ASR_MAX_FILE_SIZE_MB: int = 10
    DASHSCOPE_API_KEY: str = ""
    DASHSCOPE_BASE_URL: str = "https://dashscope.aliyuncs.com/api/v1"
    DASHSCOPE_ASR_MODEL: str = "qwen3-asr-flash"

    REMINDER_ENABLE_SCHEDULER: bool = True
    REMINDER_TIME: str = "20:00"
    REMINDER_TIMEZONE: str = "Asia/Shanghai"
    REMINDER_SCAN_DAYS_AHEAD: int = 1

    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = ""
    MYSQL_DB: str = "daily_assistant"
    MYSQL_CHARSET: str = "utf8mb4"

    DEMO_ENABLE_RESET: bool = True
    DEMO_ENABLE_UPDATE_EXECUTE: bool = False

    @property
    def cors_origins(self) -> list[str]:
        return [item.strip() for item in self.CORS_ORIGINS.split(",") if item.strip()]

    @property
    def llm_provider(self) -> str:
        provider = self.LLM_PROVIDER.strip().lower()
        return provider if provider in {"kimi", "openai"} else "kimi"

    @property
    def llm_api_key(self) -> str:
        if self.llm_provider == "openai":
            return self.OPENAI_API_KEY
        return self.KIMI_API_KEY or self.OPENAI_API_KEY

    @property
    def llm_base_url(self) -> str:
        if self.llm_provider == "openai":
            return self.OPENAI_BASE_URL
        return self.KIMI_BASE_URL

    @property
    def llm_model(self) -> str:
        if self.llm_provider == "openai":
            return self.OPENAI_MODEL
        return self.KIMI_MODEL

    @property
    def reminder_timezone(self) -> ZoneInfo:
        try:
            return ZoneInfo(self.REMINDER_TIMEZONE)
        except Exception:
            return ZoneInfo("Asia/Shanghai")


@lru_cache
def get_settings() -> Settings:
    return Settings()
