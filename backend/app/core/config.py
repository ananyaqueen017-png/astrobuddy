
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Application
    app_name: str = "AstroBuddy API"
    api_v1_prefix: str = "/api/v1"
    supabase_jwt_secret: str = ""
    database_url: str = ""
    # CORS
    cors_origins: str = "http://localhost:3000"

    @property
    def cors_origin_list(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.cors_origins.split(",")
            if origin.strip()
        ]

    # Astrology engine
    swe_ephe_path: str = ""
    ephemeris_mode: str = "swiss"
    dasha_year_days: float = 365.25
    # LLM
    llm_provider: str = ""
    anthropic_api_key: str = ""
    gemini_api_key: str = ""
    llm_model: str = ""
    llm_timeout_seconds: float = 30.0


@lru_cache
def get_settings() -> Settings:
    return Settings()

