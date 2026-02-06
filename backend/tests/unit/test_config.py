from app.core.config import Settings


def test_kimi_provider_resolution():
    settings = Settings(
        LLM_PROVIDER="kimi",
        KIMI_API_KEY="kimi-key",
        KIMI_BASE_URL="https://api.moonshot.cn/v1",
        KIMI_MODEL="kimi-k2-turbo-preview",
    )
    assert settings.llm_provider == "kimi"
    assert settings.llm_api_key == "kimi-key"
    assert settings.llm_base_url == "https://api.moonshot.cn/v1"
    assert settings.llm_model == "kimi-k2-turbo-preview"


def test_openai_provider_resolution():
    settings = Settings(
        LLM_PROVIDER="openai",
        OPENAI_API_KEY="openai-key",
        OPENAI_BASE_URL="https://api.openai.com/v1",
        OPENAI_MODEL="gpt-4o-mini",
    )
    assert settings.llm_provider == "openai"
    assert settings.llm_api_key == "openai-key"
    assert settings.llm_base_url == "https://api.openai.com/v1"
    assert settings.llm_model == "gpt-4o-mini"

