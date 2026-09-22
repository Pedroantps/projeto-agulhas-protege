"""Alertas produzidos a partir de leituras de nível."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import TIMESTAMP, Enum, ForeignKey, Index, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampCreatedAt, UUIDPrimaryKey
from app.models.leitura import NivelRiscoEnum

if TYPE_CHECKING:
    from app.models.estacao import EstacaoMonitoramento
    from app.models.leitura import LeituraNivel
    from app.models.ocorrencia import Ocorrencia
    from app.models.usuario import Usuario


class Alerta(Base):
    """Evento de risco associado a uma leitura."""

    __tablename__ = "alertas"
    __table_args__ = (
        Index("idx_alertas_ativos", "estacao_id", postgresql_where=text("encerrado_em IS NULL")),
    )

    id: Mapped[UUIDPrimaryKey]
    estacao_id: Mapped[UUID] = mapped_column(
        ForeignKey("estacoes_monitoramento.id", ondelete="RESTRICT"), nullable=False
    )
    leitura_id: Mapped[UUID] = mapped_column(
        ForeignKey("leituras_nivel.id", ondelete="RESTRICT"), nullable=False
    )
    nivel_risco: Mapped[NivelRiscoEnum] = mapped_column(
        Enum(NivelRiscoEnum, name="nivel_risco_enum"), nullable=False
    )
    encerrado_por: Mapped[UUID | None] = mapped_column(ForeignKey("usuarios.id"))
    criado_em: Mapped[TimestampCreatedAt]
    encerrado_em: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))

    estacao: Mapped[EstacaoMonitoramento] = relationship(back_populates="alertas")
    leitura: Mapped[LeituraNivel] = relationship(back_populates="alertas")
    encerrado_por_usuario: Mapped[Usuario | None] = relationship(
        back_populates="alertas_encerrados"
    )
    ocorrencias: Mapped[list[Ocorrencia]] = relationship(back_populates="alerta")
