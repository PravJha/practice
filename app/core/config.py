from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    llm_provider: str = "mock"
    openai_api_key: str = ""
    gemini_api_key: str = ""
    retry_max_attempts: int = 3
    retry_min_wait_seconds: float = 1.0
    retry_max_wait_seconds: float = 10.0
    log_level: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
