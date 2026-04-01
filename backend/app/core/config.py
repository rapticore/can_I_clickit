from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Can I Click It?"
    app_version: str = "1.0.0"
    debug: bool = False

    database_url: str = ""
    redis_url: str = ""
    elasticsearch_url: str = "http://localhost:9200"

    api_key_header: str = "X-API-Key"
    api_keys: list[str] = []

    anthropic_api_key: str = ""
    anthropic_model_fast: str = "claude-3-5-haiku-20241022"
    anthropic_model_complex: str = "claude-sonnet-4-20250514"

    virustotal_api_key: str = ""
    phishtank_api_key: str = ""

    free_tier_daily_scans: int = 5
    cache_ttl_seconds: int = 2592000  # 30 days

    enable_live_link_checks: bool = False
    max_live_url_lookups: int = 2

    cors_origins: list[str] = []

    jwt_secret_key: str = ""
    jwt_algorithm: str = "HS256"
    jwt_expiry_minutes: int = 1440

    aws_region: str = "us-east-1"
    s3_bucket: str = "clickit-data"

    log_level: str = "INFO"

    model_config = {"env_file": ".env", "env_prefix": "CLICKIT_"}

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, value: str) -> str:
        if not value:
            raise ValueError("CLICKIT_DATABASE_URL is required. Provide a PostgreSQL connection string.")
        normalized = value.lower()
        if normalized.startswith("sqlite"):
            raise ValueError("SQLite is not supported. Configure CLICKIT_DATABASE_URL to PostgreSQL.")
        if not normalized.startswith("postgresql+asyncpg://"):
            raise ValueError("Only postgresql+asyncpg URLs are supported for CLICKIT_DATABASE_URL.")
        return value

    @field_validator("redis_url")
    @classmethod
    def validate_redis_url(cls, value: str) -> str:
        if not value:
            raise ValueError("CLICKIT_REDIS_URL is required. Provide a Redis connection string.")
        return value

    @field_validator("jwt_secret_key")
    @classmethod
    def validate_jwt_secret_key(cls, value: str, info) -> str:
        debug = info.data.get("debug", False)
        if not value:
            if debug:
                return "dev-jwt-secret-not-for-production"
            raise ValueError(
                "CLICKIT_JWT_SECRET_KEY is required when debug is disabled. "
                "Set a strong random secret."
            )
        return value

    @field_validator("cors_origins")
    @classmethod
    def validate_cors_origins(cls, value: list[str], info) -> list[str]:
        debug = info.data.get("debug", False)
        if not debug and "*" in value:
            raise ValueError(
                "Wildcard '*' in CLICKIT_CORS_ORIGINS is not allowed when debug is disabled. "
                "Specify explicit origins."
            )
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
