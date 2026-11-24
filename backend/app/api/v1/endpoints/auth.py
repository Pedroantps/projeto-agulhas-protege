"""Endpoints de autenticação: login, refresh e logout."""

from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import get_current_user, get_db
from app.core.config import settings
from app.core.security import (
    clear_auth_cookies,
    create_access_token,
    create_refresh_token,
    hash_refresh_token,
    set_auth_cookies,
    verify_password,
)
from app.models.refresh_token import RefreshToken
from app.models.usuario import Usuario
from app.schemas.auth import LoginRequest, LoginResponse, UsuarioAtualResponse

router = APIRouter(prefix="/auth", tags=["Autenticação"])
limiter = Limiter(key_func=get_remote_address)


@router.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    summary="Autenticar operador",
)
@limiter.limit("5/minute")
async def login(
    request: Request,
    payload: LoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> LoginResponse:
    """Autentica o usuário com email + senha.

    Emite access token (30min) e refresh token (7 dias) como cookies httpOnly.
    Rate limit: 5/min por IP.
    """
    # 1. Buscar usuário (mensagem genérica para não revelar se email existe)
    result = await db.execute(select(Usuario).where(Usuario.email == payload.email))
    usuario = result.scalar_one_or_none()

    if not usuario or not usuario.ativo or not verify_password(payload.senha, usuario.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha inválidos.",
        )

    # 2. Gerar tokens
    access_token = create_access_token(data={"sub": str(usuario.id), "role": usuario.perfil.value})
    refresh_token = create_refresh_token()

    # 3. Persistir hash do refresh token
    expira_em = datetime.now(UTC) + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    token_db = RefreshToken(
        usuario_id=usuario.id,
        token_hash=hash_refresh_token(refresh_token),
        expira_em=expira_em,
    )
    db.add(token_db)
    await db.commit()

    # 4. Setar cookies
    set_auth_cookies(response, access_token, refresh_token)

    return LoginResponse(
        nome=usuario.nome,
        perfil=usuario.perfil.value,
        mensagem="Login realizado com sucesso.",
    )


@router.get("/me", response_model=UsuarioAtualResponse, summary="Usuário autenticado")
async def me(usuario: Usuario = Depends(get_current_user)) -> UsuarioAtualResponse:
    """Devolve nome e perfil do usuário do cookie de sessão (401 se não houver sessão)."""
    return UsuarioAtualResponse(nome=usuario.nome, perfil=usuario.perfil.value)


@router.post("/refresh", summary="Renovar sessão")
@limiter.limit("10/minute")
async def refresh(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    """Refresh Token Rotation: valida o token atual, revoga e emite um novo par.

    Rate limit: 10/min por IP.
    """
    token = request.cookies.get("refresh_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sessão expirada.")

    token_hash = hash_refresh_token(token)
    result = await db.execute(
        select(RefreshToken)
        .where(RefreshToken.token_hash == token_hash)
        .where(RefreshToken.revogado == False)  # noqa: E712
    )
    stored = result.scalar_one_or_none()

    if not stored or stored.expira_em < datetime.now(UTC):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sessão inválida.")

    # Revogar token atual
    await db.execute(update(RefreshToken).where(RefreshToken.id == stored.id).values(revogado=True))

    # Carregar usuário
    result_user = await db.execute(select(Usuario).where(Usuario.id == stored.usuario_id))
    usuario = result_user.scalar_one()

    # Gerar novo par
    new_access = create_access_token(data={"sub": str(usuario.id), "role": usuario.perfil.value})
    new_refresh = create_refresh_token()
    expira_em = datetime.now(UTC) + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)

    new_token_db = RefreshToken(
        usuario_id=usuario.id,
        token_hash=hash_refresh_token(new_refresh),
        expira_em=expira_em,
    )
    db.add(new_token_db)
    await db.commit()

    set_auth_cookies(response, new_access, new_refresh)
    return {"mensagem": "Sessão renovada com sucesso."}


@router.post("/logout", summary="Encerrar sessão")
async def logout(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    """Revoga refresh token no banco e limpa cookies."""
    token = request.cookies.get("refresh_token")
    if token:
        token_hash = hash_refresh_token(token)
        await db.execute(
            update(RefreshToken).where(RefreshToken.token_hash == token_hash).values(revogado=True)
        )
        await db.commit()

    clear_auth_cookies(response)
    return {"mensagem": "Logout realizado com sucesso."}
