"""Serviço de consulta de leituras hidrológicas históricas."""

from datetime import UTC, datetime, timedelta
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.estacao import EstacaoMonitoramento
from app.models.leitura import LeituraNivel


async def obter_historico_leituras(
    db: AsyncSession,
    estacao_id: UUID,
    horas: int = 24,
) -> list[LeituraNivel]:
    """Busca série temporal de leituras ordenadas cronologicamente.

    Query 100% parametrizada via prepared statement do SQLAlchemy.
    Valida se a estação existe e está ativa antes de consultar a série.
    """
    stmt_estacao = select(EstacaoMonitoramento).where(
        EstacaoMonitoramento.id == estacao_id,
        EstacaoMonitoramento.ativa == True,  # noqa: E712
    )
    result_estacao = await db.execute(stmt_estacao)
    estacao = result_estacao.scalar_one_or_none()

    if not estacao:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Estação de monitoramento não encontrada.",
        )

    inicio = datetime.now(UTC) - timedelta(hours=horas)
    stmt_leituras = (
        select(LeituraNivel)
        .where(
            LeituraNivel.estacao_id == estacao_id,
            LeituraNivel.data_hora >= inicio,
        )
        .order_by(LeituraNivel.data_hora.asc())
    )
    result_leituras = await db.execute(stmt_leituras)
    return list(result_leituras.scalars().all())
