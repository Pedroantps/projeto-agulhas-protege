"""Instância principal do FastAPI com middleware stack configurado."""

import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import TypedDict

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.middleware import logging_middleware, security_headers_middleware
from app.services.coleta import agendador


class HealthResponse(TypedDict):
    """Contrato da resposta do health check."""

    status: str
    versao: str


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Inicia e encerra a coleta periódica de dados reais junto com a API."""
    tarefa: asyncio.Task[None] | None = agendador.iniciar()
    try:
        yield
    finally:
        await agendador.parar(tarefa)


app = FastAPI(
    lifespan=lifespan,
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


def _servir_frontend(pasta: Path) -> None:
    """Serve o frontend compilado (SPA) a partir da própria API, no mesmo domínio."""
    assets = pasta / "assets"
    if assets.is_dir():
        app.mount("/assets", StaticFiles(directory=assets), name="assets")
    raiz = pasta.resolve()

    @app.get("/{caminho:path}", include_in_schema=False)
    async def spa(caminho: str) -> FileResponse:
        if caminho.startswith(("api/", "health")):
            raise HTTPException(status_code=404, detail="Não encontrado.")
        candidato = (raiz / caminho).resolve()
        if caminho and candidato.is_file() and raiz in candidato.parents:
            return FileResponse(candidato)
        return FileResponse(raiz / "index.html")


if settings.FRONTEND_DIST_DIR and (Path(settings.FRONTEND_DIST_DIR) / "index.html").is_file():
    _servir_frontend(Path(settings.FRONTEND_DIST_DIR))
