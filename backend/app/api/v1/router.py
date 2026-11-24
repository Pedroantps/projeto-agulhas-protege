"""Agregador de rotas da API v1."""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, coleta, estacoes, leituras, ocorrencias, sesmaria

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(coleta.router)
api_router.include_router(estacoes.router)
api_router.include_router(leituras.router)
api_router.include_router(ocorrencias.router)
api_router.include_router(sesmaria.router)

__all__ = ["api_router"]
