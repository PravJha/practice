import pytest


def test_default_settings(monkeypatch):
    # Explicitly pin to mock so tests never hit a real LLM regardless of .env
    monkeypatch.setenv("LLM_PROVIDER", "mock")
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    from app.core.config import Settings
    s = Settings()
    assert s.llm_provider == "mock"
    assert s.retry_max_attempts == 3
    assert s.retry_min_wait_seconds == 1.0
    assert s.retry_max_wait_seconds == 10.0
    assert s.log_level == "INFO"


def test_settings_overridden_by_env(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("RETRY_MAX_ATTEMPTS", "5")

    from app.core.config import Settings
    s = Settings()
    assert s.llm_provider == "openai"
    assert s.retry_max_attempts == 5
