import os
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=["../../.env", ".env"],
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: int = 20  # INFO
    SECRET_KEY: str = "change-me-in-production"

    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_WORKERS: int = 4
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    DATABASE_URL: str = "postgresql+asyncpg://pip:password@localhost:5432/pip"
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "neo4j_password"
    REDIS_URL: str = "redis://localhost:6379/0"
    QDRANT_URL: str = "http://localhost:6333"

    JWT_SECRET_KEY: str = "change-me-use-openssl-rand-hex-32"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o"
    OPENAI_MINI_MODEL: str = "gpt-4o-mini"

    AI_SERVICE_URL: str = "http://localhost:8001"
    OLLAMA_BASE_URL: str = "http://localhost:11434/v1"
    OLLAMA_MODEL: str = "gemma2:2b"

    STORAGE_BACKEND: str = "local"
    STORAGE_LOCAL_PATH: str = "./storage"

    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = ""

    DISABLE_MEETING_REMINDER_SCHEDULER: bool = False

    def validate_production(self) -> None:
        """Fail fast in production when anyone relies on default secrets.

        This prevents a deployment with forgeable JWTs or an unset database
        from starting silently.
        """
        if self.ENVIRONMENT.lower() != "production":
            return

        problems: list[str] = []
        jwt_default = "change-me-use-openssl-rand-hex-32"
        if not self.JWT_SECRET_KEY or self.JWT_SECRET_KEY == jwt_default:
            problems.append("JWT_SECRET_KEY must be set to a strong random value in production")
        db_default = "pip:password@localhost"
        if db_default in self.DATABASE_URL:
            problems.append("DATABASE_URL still points at the default local database")
        if not os.getenv("JWT_SECRET_KEY") and os.getenv("ENVIRONMENT", "").lower() == "production":
            problems.append("JWT_SECRET_KEY must come from the environment in production")

        if problems:
            raise RuntimeError(
                "Refusing to start in production with insecure defaults: "
                + "; ".join(problems)
            )


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.validate_production()
    return settings


settings = get_settings()
