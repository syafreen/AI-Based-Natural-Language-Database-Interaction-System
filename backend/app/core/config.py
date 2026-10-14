from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI-Based Natural Language Database Interaction System"
    environment: Literal["local", "test", "production"] = "local"
    log_level: str = "INFO"

    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/ai_sql_assistant"
    )
    database_statement_timeout_ms: int = 5000

    openai_api_key: str = ""
    openai_base_url: str | None = None
    openai_model: str = "gpt-4.1-mini"
    ai_temperature: float = 0
    enable_ai_summary: bool = True

    max_query_limit: int = 100
    cors_origins: list[str] = ["http://localhost:5173"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
