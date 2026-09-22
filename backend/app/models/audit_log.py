"""Trilha de auditoria imutável das operações críticas."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any
from uuid import UUID

from sqlalchemy import TIMESTAMP, BigInteger, ForeignKey, Index, String, desc, func
from sqlalchemy.dialects.postgresql import INET, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.usuario import Usuario


class AuditLog(Base):
    """Snapshot anterior e posterior de uma alteração auditável."""

    __tablename__ = "audit_log"
    __table_args__ = (
        Index("idx_audit_log_entidade", "entidade", "entidade_id", desc("criado_em")),
        Index("idx_audit_log_usuario", "usuario_id", desc("criado_em")),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    usuario_id: Mapped[UUID | None] = mapped_column(ForeignKey("usuarios.id"))
    acao: Mapped[str] = mapped_column(String(50), nullable=False)
    entidade: Mapped[str] = mapped_column(String(100), nullable=False)
    entidade_id: Mapped[UUID] = mapped_column(nullable=False)
    dados_anteriores: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    dados_novos: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    ip_address: Mapped[str | None] = mapped_column(INET)
    request_id: Mapped[str | None] = mapped_column(String(36))
    criado_em: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )

    usuario: Mapped[Usuario | None] = relationship(back_populates="registros_auditoria")
