"""Schemas Pydantic da aplicação."""

from app.schemas.auth import LoginRequest, LoginResponse
from app.schemas.cotas import AtualizarCotasRequest, CotasResponse
from app.schemas.estacao import CotasSchema, StatusAtualResponse
from app.schemas.leitura import HistoricoQuery, LeituraHistoricoResponse
from app.schemas.ocorrencia import CriarOcorrenciaRequest, OcorrenciaResponse

__all__ = [
    "AtualizarCotasRequest",
    "CotasResponse",
    "CotasSchema",
    "CriarOcorrenciaRequest",
    "HistoricoQuery",
    "LeituraHistoricoResponse",
    "LoginRequest",
    "LoginResponse",
    "OcorrenciaResponse",
    "StatusAtualResponse",
]
