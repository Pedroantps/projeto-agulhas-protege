"""Testes unitários das funções de segurança (hashing, JWT e cookies)."""

from fastapi import Response
from jose import jwt

from app.core.config import settings
from app.core.security import (
    clear_auth_cookies,
    create_access_token,
    create_refresh_token,
    hash_password,
    hash_refresh_token,
    set_auth_cookies,
    verify_password,
)


def test_hash_password_diferente_do_plain() -> None:
    hashed = hash_password("minha_senha")
    assert hashed != "minha_senha"


def test_verify_password_correto() -> None:
    hashed = hash_password("minha_senha")
    assert verify_password("minha_senha", hashed) is True


def test_verify_password_errado() -> None:
    hashed = hash_password("minha_senha")
    assert verify_password("senha_errada", hashed) is False


def test_access_token_decodificavel() -> None:
    token = create_access_token({"sub": "user-id-123", "role": "ADMINISTRADOR"})
    payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    assert payload["sub"] == "user-id-123"
    assert payload["role"] == "ADMINISTRADOR"
    assert "exp" in payload
    assert "iat" in payload


def test_access_token_expirado_levanta_erro() -> None:
    from datetime import UTC, datetime, timedelta

    import pytest
    from jose import JWTError

    token = create_access_token({"sub": "abc", "exp": datetime.now(UTC) - timedelta(seconds=1)})
    with pytest.raises(JWTError):
        jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])


def test_create_refresh_token_gera_string_opaca() -> None:
    token1 = create_refresh_token()
    token2 = create_refresh_token()
    assert token1 != token2
    assert len(token1) >= 64


def test_hash_refresh_token_deterministico() -> None:
    token = "meu-refresh-token-secreto"  # noqa: S105
    assert hash_refresh_token(token) == hash_refresh_token(token)
    assert len(hash_refresh_token(token)) == 64  # SHA-256 hex


def test_set_e_clear_auth_cookies() -> None:
    response = Response()
    set_auth_cookies(response, "test-access-token", "test-refresh-token")
    raw_headers = response.raw_headers
    set_cookie_headers = [h[1].decode() for h in raw_headers if h[0].lower() == b"set-cookie"]
    assert len(set_cookie_headers) == 2
    assert any("access_token=test-access-token" in h for h in set_cookie_headers)
    assert any("refresh_token=test-refresh-token" in h for h in set_cookie_headers)

    clear_response = Response()
    clear_auth_cookies(clear_response)
    clear_headers = [
        h[1].decode() for h in clear_response.raw_headers if h[0].lower() == b"set-cookie"
    ]
    assert len(clear_headers) == 2
