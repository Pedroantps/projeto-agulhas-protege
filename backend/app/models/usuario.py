"""Usuários e perfis de acesso da aplicação."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import TIMESTAMP, Boolean, Enum, String, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampCreatedAt, UUIDPrimaryKey

if TYPE_CHECKING:
    from app.models.alerta import Alerta
    from app.models.audit_log import AuditLog
    from app.models.ocorrencia import Ocorrencia
    from app.models.refresh_token import RefreshToken


class PerfilUsuario(StrEnum):
    """Perfis permitidos pelo RBAC."""

    ADMINISTRADOR = "ADMINISTRADOR"
    OPERADOR_DEFESA_CIVIL = "OPERADOR_DEFESA_CIVIL"


class Usuario(Base):
    """Operador autenticável do sistema."""

    __tablename__ = "usuarios"

    id: Mapped[UUIDPrimaryKey]
    nome: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(String(254), nullable=False, unique=True)
    senha_hash: Mapped[str] = mapped_column(nullable=False)
    perfil: Mapped[PerfilUsuario] = mapped_column(
        Enum(PerfilUsuario, name="perfil_usuario"), nullable=False
    )
    ativo: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default=text("true")
    )
    criado_em: Mapped[TimestampCreatedAt]
    atualizado_em: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    alertas_encerrados: Mapped[list[Alerta]] = relationship(back_populates="encerrado_por_usuario")
    ocorrencias: Mapped[list[Ocorrencia]] = relationship(back_populates="usuario")
    refresh_tokens: Mapped[list[RefreshToken]] = relationship(
        back_populates="usuario", cascade="all, delete-orphan"
    )
    registros_auditoria: Mapped[list[AuditLog]] = relationship(back_populates="usuario")
