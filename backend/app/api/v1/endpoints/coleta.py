"""Endpoints de acompanhamento e acionamento manual da coleta de dados reais."""

from datetime import datetime

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import get_db, require_admin
from app.core.config import settings
from app.models.coleta import ColetaBacia
from app.models.leitura import LeituraNivel
from app.models.usuario import Usuario
from app.services.coleta.coletor import executar_coleta

router = APIRouter(prefix="/coleta", tags=["Coleta de dados reais"])
limiter = Limiter(key_func=get_remote_address)


class StatusColetaResponse(BaseModel):
    """Situação da coleta automática."""

    habilitada: bool
    intervalo_minutos: int
    ultima_coleta: datetime | None
    ultima_leitura: datetime | None
    total_leituras: int
    fontes: list[str]


class ExecucaoColetaResponse(BaseModel):
    """Resultado de uma coleta acionada manualmente."""

    leituras_novas: int
    fontes_ok: list[str]
    erros: dict[str, str]


@router.get("/status", response_model=StatusColetaResponse, summary="Status da coleta automática")
@limiter.limit("60/minute")
async def status_coleta(
    request: Request, db: AsyncSession = Depends(get_db)
) -> StatusColetaResponse:
    """Endpoint público: mostra de onde vêm os dados e quando foram atualizados."""
    ultima = (await db.execute(select(func.max(ColetaBacia.coletado_em)))).scalar_one_or_none()
    leitura = (await db.execute(select(func.max(LeituraNivel.data_hora)))).scalar_one_or_none()
    total = (await db.execute(select(func.count(LeituraNivel.id)))).scalar_one_or_none()
    return StatusColetaResponse(
        habilitada=settings.COLETA_HABILITADA,
        intervalo_minutos=settings.COLETA_INTERVALO_MINUTOS,
        ultima_coleta=ultima if isinstance(ultima, datetime) else None,
        ultima_leitura=leitura if isinstance(leitura, datetime) else None,
        total_leituras=int(total) if isinstance(total, int) else 0,
        fontes=[
            f"CEMADEN estação {settings.CEMADEN_ESTACAO_CODIGO} (nível, chuva e câmera)",
            "Open-Meteo (chuva observada e prevista)",
            "ONS Dados Abertos (vazão do Funil)",
        ],
    )


@router.post(
    "/executar", response_model=ExecucaoColetaResponse, summary="Executar coleta agora (admin)"
)
@limiter.limit("6/minute")
async def executar(
    request: Request, _admin: Usuario = Depends(require_admin)
) -> ExecucaoColetaResponse:
    """Dispara uma rodada de coleta imediatamente. Requer perfil ADMINISTRADOR."""
    resultado = await executar_coleta()
    return ExecucaoColetaResponse(
        leituras_novas=resultado.leituras_novas,
        fontes_ok=resultado.fontes_ok,
        erros=resultado.erros,
    )
