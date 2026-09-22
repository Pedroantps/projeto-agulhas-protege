"""Funções de segurança: hashing de senha, JWT e cookies."""

import hashlib
import secrets
from datetime import UTC, datetime, timedelta
from typing import Any

import bcrypt
from fastapi import Response
from jose import jwt

from app.core.config import settings

# ── Senha ──────────────────────────────────────────────────────────────────


def hash_password(plain: str) -> str:
    """Retorna hash bcrypt da senha em texto plano."""
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt(rounds=12)).decode()


def verify_password(plain: str, hashed: str) -> bool:
    """Verifica senha contra hash bcrypt."""
    return bcrypt.checkpw(plain.encode(), hashed.encode())


# ── JWT ────────────────────────────────────────────────────────────────────


def create_access_token(data: dict[str, Any]) -> str:
    """Gera JWT de acesso com expiração configurável.

    Inclui sub (user_id) e role (perfil).
    """
    payload = data.copy()
    if "exp" not in payload:
        payload["exp"] = datetime.now(UTC) + timedelta(
            minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )
    if "iat" not in payload:
        payload["iat"] = datetime.now(UTC)
    return str(jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM))


def create_refresh_token() -> str:
    """Gera token de refresh como string aleatória segura (não JWT).

    O token em si é opaco — apenas seu hash é armazenado no banco.
    """
    return secrets.token_urlsafe(64)


def hash_refresh_token(token: str) -> str:
    """Retorna SHA-256 hex do refresh token para armazenamento seguro."""
    return hashlib.sha256(token.encode()).hexdigest()


# ── Cookies ────────────────────────────────────────────────────────────────


def set_auth_cookies(response: Response, access_token: str, refresh_token: str) -> None:
    """Define ambos os cookies com máxima segurança.

    - httpOnly: inacessível via JavaScript
    - secure: HTTPS
    - samesite: proteção CSRF
    """
    # Access Token — enviado em TODAS as rotas
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        max_age=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
    )
    # Refresh Token — enviado APENAS para /api/v1/auth/*
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        max_age=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 86400,
        path="/api/v1/auth",
    )


def clear_auth_cookies(response: Response) -> None:
    """Remove ambos os cookies (logout)."""
    response.delete_cookie("access_token", path="/")
    response.delete_cookie("refresh_token", path="/api/v1/auth")
