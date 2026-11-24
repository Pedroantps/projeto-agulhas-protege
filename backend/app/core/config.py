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

    # Coleta de dados reais (CEMADEN, Open-Meteo, ONS) executada pelo próprio backend.
    COLETA_HABILITADA: bool = True
    COLETA_INTERVALO_MINUTOS: int = Field(default=10, ge=1)
    CEMADEN_ESTACAO_ID: int = 8799
    CEMADEN_ESTACAO_CODIGO: str = "330420118H"
    HTTP_TIMEOUT_SEGUNDOS: float = 15.0

    # URL pública do painel (usada nas mensagens de alerta) e pasta do frontend compilado.
    PUBLIC_URL: str = "http://localhost:5173"
    FRONTEND_DIST_DIR: str | None = None

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

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def normalizar_driver_postgres(cls, value: object) -> object:
        """Aceita URLs de provedores (postgres://, postgresql://) e força o driver psycopg."""
        if isinstance(value, str):
            for prefixo in ("postgres://", "postgresql://"):
                if value.startswith(prefixo):
                    return "postgresql+psycopg://" + value[len(prefixo) :]
        return value

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
