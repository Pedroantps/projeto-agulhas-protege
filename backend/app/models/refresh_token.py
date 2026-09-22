"""Refresh tokens persistidos somente por seu hash."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import TIMESTAMP, Boolean, ForeignKey, Index, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampCreatedAt, UUIDPrimaryKey

if TYPE_CHECKING:
    from app.models.usuario import Usuario


class RefreshToken(Base):
    """Token renovável associado a uma sessão de usuário."""

    __tablename__ = "refresh_tokens"
    __table_args__ = (
        Index(
            "idx_refresh_tokens_usuario",
            "usuario_id",
            postgresql_where=text("NOT revogado"),
        ),
    )

    id: Mapped[UUIDPrimaryKey]
    usuario_id: Mapped[UUID] = mapped_column(
        ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False
    )
    token_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    expira_em: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)
    revogado: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default=text("false")
    )
    criado_em: Mapped[TimestampCreatedAt]

    usuario: Mapped[Usuario] = relationship(back_populates="refresh_tokens")
