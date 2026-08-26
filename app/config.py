from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "local"
    llm_primary_provider: str = "mock-oci"
    llm_fallback_provider: str = "mock-openai"
    llm_request_budget_usd: float = 0.05
    oracle_base_url: str = "https://example.invalid"
    oracle_client_id: str = "replace-me"
    oracle_client_secret: str = "replace-me"
    database_url: str = "postgresql://climate:climate@localhost:5432/climate_ai"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
