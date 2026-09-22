"""Dependências FastAPI para extração e validação do usuário autenticado."""

from uuid import UUID

from fastapi import Cookie, Depends, HTTPException, status
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db
from app.models.usuario import PerfilUsuario, Usuario


async def get_current_user(
    access_token: str | None = Cookie(default=None),
    db: AsyncSession = Depends(get_db),
) -> Usuario:
    """Extrai o JWT do cookie httpOnly e retorna o usuário autenticado.

    Levanta 401 para token ausente, expirado ou inválido.
    """
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Autenticação necessária.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = jwt.decode(
            access_token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        user_id: str | None = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido.",
            )
    except JWTError as err:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado ou inválido.",
        ) from err

    try:
        user_uuid = UUID(user_id)
    except (ValueError, TypeError) as err:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido.",
        ) from err

    result = await db.execute(select(Usuario).where(Usuario.id == user_uuid))
    usuario = result.scalar_one_or_none()

    if not usuario or not usuario.ativo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado ou inativo.",
        )

    return usuario


async def require_operador(
    usuario: Usuario = Depends(get_current_user),
) -> Usuario:
    """Guard RBAC: requer OPERADOR_DEFESA_CIVIL ou ADMINISTRADOR."""
    roles_permitidos = {PerfilUsuario.OPERADOR_DEFESA_CIVIL, PerfilUsuario.ADMINISTRADOR}
    if usuario.perfil not in roles_permitidos:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito a operadores da Defesa Civil.",
        )
    return usuario


async def require_admin(
    usuario: Usuario = Depends(get_current_user),
) -> Usuario:
    """Guard RBAC: requer ADMINISTRADOR."""
    if usuario.perfil != PerfilUsuario.ADMINISTRADOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito ao perfil de Administrador.",
        )
    return usuario


__all__ = [
    "get_current_user",
    "get_db",
    "require_admin",
    "require_operador",
]
