"""Configuração central da aplicação via pydantic-settings."""

from functools import lru_cache
from typing import Literal

from pydantic import AnyHttpUrl, Field, PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Variáveis de ambiente validadas durante a inicialização."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    DATABASE_URL: PostgresDsn

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    COOKIE_SECURE: bool = True
    COOKIE_SAMESITE: Literal["lax", "strict", "none"] = "lax"

    CORS_ORIGINS: list[AnyHttpUrl] = Field(
        default_factory=lambda: [AnyHttpUrl("http://localhost:5173")]
    )

    RATE_LIMIT_PER_MINUTE: int = Field(default=60, ge=1)

    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    @field_validator("JWT_SECRET_KEY")
    @classmethod
    def jwt_secret_must_be_strong(cls, value: str) -> str:
        """Rejeita chaves JWT curtas demais para uso seguro."""
        if len(value) < 32:
            message = "JWT_SECRET_KEY deve ter pelo menos 32 caracteres."
            raise ValueError(message)
        return value


@lru_cache
def get_settings() -> Settings:
    """Cria e memoriza a configuração do processo."""
    return Settings()


settings = get_settings()
