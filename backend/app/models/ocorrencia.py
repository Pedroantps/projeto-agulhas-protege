"""Ocorrências de campo registradas pela Defesa Civil."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import TIMESTAMP, Enum, ForeignKey, String, Text, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampCreatedAt, UUIDPrimaryKey

if TYPE_CHECKING:
    from app.models.alerta import Alerta
    from app.models.estacao import EstacaoMonitoramento
    from app.models.usuario import Usuario


class StatusOcorrencia(StrEnum):
    """Estados possíveis do atendimento de uma ocorrência."""

    ABERTA = "ABERTA"
    EM_ANDAMENTO = "EM_ANDAMENTO"
    ENCERRADA = "ENCERRADA"


class Ocorrencia(Base):
    """Registro operacional de uma situação observada em campo."""

    __tablename__ = "ocorrencias"

    id: Mapped[UUIDPrimaryKey]
    usuario_id: Mapped[UUID] = mapped_column(
        ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=False
    )
    estacao_id: Mapped[UUID] = mapped_column(
        ForeignKey("estacoes_monitoramento.id", ondelete="RESTRICT"), nullable=False
    )
    alerta_id: Mapped[UUID | None] = mapped_column(ForeignKey("alertas.id"))
    localizacao: Mapped[str] = mapped_column(String(300), nullable=False)
    descricao: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[StatusOcorrencia] = mapped_column(
        Enum(StatusOcorrencia, name="status_ocorrencia"),
        nullable=False,
        default=StatusOcorrencia.ABERTA,
        server_default=text("'ABERTA'"),
    )
    criado_em: Mapped[TimestampCreatedAt]
    atualizado_em: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    usuario: Mapped[Usuario] = relationship(back_populates="ocorrencias")
    estacao: Mapped[EstacaoMonitoramento] = relationship(back_populates="ocorrencias")
    alerta: Mapped[Alerta | None] = relationship(back_populates="ocorrencias")
