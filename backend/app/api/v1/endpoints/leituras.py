"""Endpoints para consulta de séries temporais de leituras de nível."""

from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import get_db
from app.schemas.leitura import LeituraHistoricoResponse
from app.services.leitura_service import obter_historico_leituras

router = APIRouter(prefix="/leituras", tags=["Leituras"])
limiter = Limiter(key_func=get_remote_address)


@router.get(
    "/historico",
    response_model=list[LeituraHistoricoResponse],
    summary="Histórico de leituras de uma estação",
)
@limiter.limit("60/minute")
async def get_historico(
    request: Request,
    estacao_id: UUID = Query(..., description="UUID da estação de monitoramento"),
    horas: int = Query(24, ge=1, le=2160, description="Período em horas (max: 2160 = 90 dias)"),
    db: AsyncSession = Depends(get_db),
) -> list[LeituraHistoricoResponse]:
    """Endpoint público. Retorna série temporal de leituras ordenadas cronologicamente."""
    leituras = await obter_historico_leituras(db, estacao_id=estacao_id, horas=horas)
    return [
        LeituraHistoricoResponse(
            id=leitura.id,
            data_hora=leitura.data_hora,
            nivel_metros=leitura.nivel_metros,
            classificacao=leitura.classificacao.value
            if hasattr(leitura.classificacao, "value")
            else str(leitura.classificacao),
        )
        for leitura in leituras
    ]
