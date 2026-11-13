"""Application configuration loaded from environment / .env."""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Strongly-typed application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # LLM
    default_llm_provider: str = "openai"
    default_llm_model: str = "gpt-4o-mini"
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    groq_api_key: str | None = None
    ollama_base_url: str = "http://localhost:11434"

    # Database
    database_url: str = "postgresql+asyncpg://mares:mares@localhost:5432/mares"
    redis_url: str = "redis://localhost:6379/0"
    mares_memory_backend: str = "memory"

    # Orchestrator
    max_concurrent_tasks: int = 5
    task_timeout_seconds: int = 120
    max_retries: int = 3

    # Tools
    search_provider: str = "auto"
    serpapi_api_key: str | None = None
    brave_api_key: str | None = None
    search_timeout_seconds: int = 30
    python_sandbox_timeout_seconds: int = 10
    tool_failure_rate: float = 0.0

    # Research agent
    research_enable_search: bool = True
    research_search_results: int = 5

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_log_level: str = "info"
    cors_origins: str = "*"

    # Logging
    log_level: str = "INFO"
    log_format: str = "json"

    @property
    def cors_origin_list(self) -> list[str]:
        """Parse the comma-separated ``CORS_ORIGINS`` value into a list."""
        origins = [o.strip() for o in self.cors_origins.split(",") if o.strip()]
        return origins or ["*"]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]


__all__ = ["Settings", "get_settings"]
