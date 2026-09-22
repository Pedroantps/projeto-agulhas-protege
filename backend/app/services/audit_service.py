"""Serviço de auditoria imutável das operações críticas do sistema."""

from typing import Any
from uuid import UUID

from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog


async def registrar_audit_log(
    db: AsyncSession,
    *,
    usuario_id: UUID | None,
    acao: str,
    entidade: str,
    entidade_id: UUID,
    dados_anteriores: dict[str, Any] | None = None,
    dados_novos: dict[str, Any] | None = None,
    ip_address: str | None = None,
    request_id: str | None = None,
) -> None:
    """Registra operação crítica de escrita no audit_log.

    Executa flush imediato para propagar o registro sem fechar a transação principal.
    """
    stmt = insert(AuditLog).values(
        usuario_id=usuario_id,
        acao=acao,
        entidade=entidade,
        entidade_id=entidade_id,
        dados_anteriores=dados_anteriores,
        dados_novos=dados_novos,
        ip_address=ip_address,
        request_id=request_id,
    )
    await db.execute(stmt)
    await db.flush()
