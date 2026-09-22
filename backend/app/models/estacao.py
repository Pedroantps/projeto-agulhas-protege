"""Estações de monitoramento hidrológico."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Numeric, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampCreatedAt, UUIDPrimaryKey

if TYPE_CHECKING:
    from app.models.alerta import Alerta
    from app.models.leitura import LeituraNivel
    from app.models.niveis_risco import NivelRisco
    from app.models.ocorrencia import Ocorrencia


class EstacaoMonitoramento(Base):
    """Ponto físico que fornece leituras do nível de um rio."""

    __tablename__ = "estacoes_monitoramento"

    id: Mapped[UUIDPrimaryKey]
    codigo_externo: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    nome: Mapped[str] = mapped_column(String(200), nullable=False)
    rio: Mapped[str] = mapped_column(String(100), nullable=False)
    latitude: Mapped[Decimal | None] = mapped_column(Numeric(9, 6))
    longitude: Mapped[Decimal | None] = mapped_column(Numeric(9, 6))
    ativa: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default=text("true")
    )
    criado_em: Mapped[TimestampCreatedAt]

    niveis_risco: Mapped[NivelRisco | None] = relationship(back_populates="estacao", uselist=False)
    leituras: Mapped[list[LeituraNivel]] = relationship(back_populates="estacao")
    alertas: Mapped[list[Alerta]] = relationship(back_populates="estacao")
    ocorrencias: Mapped[list[Ocorrencia]] = relationship(back_populates="estacao")
