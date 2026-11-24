"""Instantâneos das coletas externas (chuva, previsão, vazão do Funil, foto da estação)."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import TIMESTAMP, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, UUIDPrimaryKey


class ColetaBacia(Base):
    """Resultado de uma rodada de coleta das fontes externas da bacia do Sesmaria."""

    __tablename__ = "coletas_bacia"

    id: Mapped[UUIDPrimaryKey]
    coletado_em: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False, index=True
    )
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
