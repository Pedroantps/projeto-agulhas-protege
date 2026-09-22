"""Instância principal do FastAPI com middleware stack configurado."""

from typing import TypedDict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.middleware import logging_middleware, security_headers_middleware


class HealthResponse(TypedDict):
    """Contrato da resposta do health check."""

    status: str
    versao: str


app = FastAPI(
    title="Agulhas Protege API",
    version="1.0.0",
    description="Sistema de Monitoramento e Alerta de Cheias — Resende-RJ",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[f"{settings.RATE_LIMIT_PER_MINUTE}/minute"],
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore[arg-type]

# O último middleware registrado é o primeiro a receber a requisição no Starlette.
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin).rstrip("/") for origin in settings.CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Request-ID"],
)
app.middleware("http")(security_headers_middleware)
app.middleware("http")(logging_middleware)

app.include_router(api_router, prefix="/api/v1")


@app.get("/health", tags=["Infraestrutura"])
async def health_check() -> HealthResponse:
    """Informa que o processo da API está saudável."""
    return {"status": "ok", "versao": app.version}
