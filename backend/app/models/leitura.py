"""Leituras temporais do nível dos rios."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import TIMESTAMP, Enum, ForeignKey, Index, Numeric, String, desc
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampCreatedAt, UUIDPrimaryKey

if TYPE_CHECKING:
    from app.models.alerta import Alerta
    from app.models.estacao import EstacaoMonitoramento


class NivelRiscoEnum(StrEnum):
    """Classificação de risco de uma leitura."""

    NORMAL = "NORMAL"
    ATENCAO = "ATENCAO"
    ALERTA = "ALERTA"
    EMERGENCIA = "EMERGENCIA"


class LeituraNivel(Base):
    """Medição do nível de uma estação em um instante."""

    __tablename__ = "leituras_nivel"
    __table_args__ = (Index("idx_leituras_estacao_data", "estacao_id", desc("data_hora")),)

    id: Mapped[UUIDPrimaryKey]
    estacao_id: Mapped[UUID] = mapped_column(
        ForeignKey("estacoes_monitoramento.id", ondelete="RESTRICT"), nullable=False
    )
    data_hora: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)
    nivel_metros: Mapped[Decimal] = mapped_column(Numeric(6, 3), nullable=False)
    classificacao: Mapped[NivelRiscoEnum] = mapped_column(
        Enum(NivelRiscoEnum, name="nivel_risco_enum"), nullable=False
    )
    fonte: Mapped[str | None] = mapped_column(String(100))
    criado_em: Mapped[TimestampCreatedAt]

    estacao: Mapped[EstacaoMonitoramento] = relationship(back_populates="leituras")
    alertas: Mapped[list[Alerta]] = relationship(back_populates="leitura")
