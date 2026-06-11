from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "DocIntel API"
    environment: str = "local"
    database_url: str = "sqlite:///./docintel.db"
    redis_url: str = "redis://localhost:6379/0"
    upload_dir: str = "storage/uploads"
    ocr_provider: str = "mock"
    rate_limit_requests: int = 120
    rate_limit_window_seconds: int = 60

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
