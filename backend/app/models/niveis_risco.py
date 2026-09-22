"""Cotas de risco configuradas por estação."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import TIMESTAMP, CheckConstraint, ForeignKey, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, UUIDPrimaryKey

if TYPE_CHECKING:
    from app.models.estacao import EstacaoMonitoramento


class NivelRisco(Base):
    """Limiares crescentes usados para classificar leituras."""

    __tablename__ = "niveis_risco"
    __table_args__ = (
        CheckConstraint(
            "cota_atencao < cota_alerta AND cota_alerta < cota_emergencia",
            name="cotas_ordem_crescente",
        ),
    )

    id: Mapped[UUIDPrimaryKey]
    estacao_id: Mapped[UUID] = mapped_column(
        ForeignKey("estacoes_monitoramento.id", ondelete="RESTRICT"),
        nullable=False,
        unique=True,
    )
    cota_atencao: Mapped[Decimal] = mapped_column(Numeric(6, 2), nullable=False)
    cota_alerta: Mapped[Decimal] = mapped_column(Numeric(6, 2), nullable=False)
    cota_emergencia: Mapped[Decimal] = mapped_column(Numeric(6, 2), nullable=False)
    atualizado_em: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    estacao: Mapped[EstacaoMonitoramento] = relationship(back_populates="niveis_risco")
