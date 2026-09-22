"""Testes unitários dos schemas de autenticação."""

import pytest
from pydantic import ValidationError

from app.schemas.auth import LoginRequest, LoginResponse


def test_login_request_valido() -> None:
    req = LoginRequest(email="operador@defesacivil.gov.br", senha="senhaSegura123")
    assert req.email == "operador@defesacivil.gov.br"
    assert req.senha == "senhaSegura123"


def test_login_request_senha_curta_invalida() -> None:
    with pytest.raises(ValidationError) as exc:
        LoginRequest(email="operador@defesacivil.gov.br", senha="123")
    assert "Senha deve ter pelo menos 6 caracteres." in str(exc.value)


def test_login_request_email_invalido() -> None:
    with pytest.raises(ValidationError):
        LoginRequest(email="email-invalido", senha="senhaSegura123")


def test_login_response_valido() -> None:
    res = LoginResponse(nome="Operador Silva", perfil="OPERADOR_DEFESA_CIVIL")
    assert res.nome == "Operador Silva"
    assert res.perfil == "OPERADOR_DEFESA_CIVIL"
    assert res.mensagem == "Login realizado com sucesso."
