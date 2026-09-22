from typing import TYPE_CHECKING

import pytest
from httpx import AsyncClient

from app.models.estacao import EstacaoMonitoramento
from app.models.usuario import Usuario

if TYPE_CHECKING:
    from tests.conftest import InMemoryAsyncSession


@pytest.mark.asyncio
async def test_login_sucesso(client: AsyncClient, usuario_seed: Usuario) -> None:
    """Login com credenciais corretas deve retornar 200 e setar cookies httpOnly."""
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "admin@defesacivil.resende.rj.gov.br",
            "senha": "Admin@2026",
        },
    )
    assert response.status_code == 200
    assert "access_token" in response.cookies
    assert "refresh_token" in response.cookies
    data = response.json()
    assert data["perfil"] == "ADMINISTRADOR"
    assert data["nome"] == usuario_seed.nome


@pytest.mark.asyncio
async def test_login_senha_errada(client: AsyncClient, usuario_seed: Usuario) -> None:
    """Login com senha errada deve retornar 401 com mensagem genérica."""
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "admin@defesacivil.resende.rj.gov.br",
            "senha": "senha_errada",
        },
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Email ou senha inválidos."


@pytest.mark.asyncio
async def test_login_usuario_inexistente(client: AsyncClient) -> None:
    """Login com email inexistente deve retornar 401 com a mesma mensagem genérica."""
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "inexistente@defesacivil.resende.rj.gov.br",
            "senha": "qualquer_senha",
        },
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Email ou senha inválidos."


@pytest.mark.asyncio
async def test_refresh_rotation(client: AsyncClient, auth_cookies: dict[str, str]) -> None:
    """Refresh token rotation revoga o token anterior e emite um novo par nos cookies."""
    response = await client.post("/api/v1/auth/refresh", cookies=auth_cookies)
    assert response.status_code == 200
    assert response.cookies["refresh_token"] != auth_cookies["refresh_token"]


@pytest.mark.asyncio
async def test_refresh_sem_cookie(client: AsyncClient) -> None:
    """Chamada de refresh sem cookie deve retornar 401."""
    response = await client.post("/api/v1/auth/refresh")
    assert response.status_code == 401
    assert response.json()["detail"] == "Sessão expirada."


@pytest.mark.asyncio
async def test_logout_limpa_cookies(client: AsyncClient, auth_cookies: dict[str, str]) -> None:
    """Logout deve responder 200 e limpar os cookies de sessão."""
    response = await client.post("/api/v1/auth/logout", cookies=auth_cookies)
    assert response.status_code == 200
    assert response.cookies.get("access_token") is None or response.cookies["access_token"] == ""


@pytest.mark.asyncio
async def test_rota_protegida_sem_token(client: AsyncClient) -> None:
    """Acesso a rota protegida sem token de autenticação deve retornar 401."""
    response = await client.post("/api/v1/ocorrencias", json={})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_operador_acessa_rota_operador(
    client: AsyncClient,
    operador_cookies: dict[str, str],
    estacoes_seed: list[EstacaoMonitoramento],
) -> None:
    """Operador autenticado consegue acessar endpoint de ocorrência."""
    response = await client.post(
        "/api/v1/ocorrencias",
        json={
            "estacao_id": str(estacoes_seed[0].id),
            "localizacao": "Rua das Acácias, 45",
            "descricao": "Monitoramento preventivo realizado pelo operador.",
        },
        cookies=operador_cookies,
    )
    assert response.status_code == 201


@pytest.mark.asyncio
async def test_operador_nao_acessa_rota_admin(
    client: AsyncClient,
    operador_cookies: dict[str, str],
    estacoes_seed: list[EstacaoMonitoramento],
) -> None:
    """Operador autenticado não pode acessar rotas restritas a administradores (403)."""
    response = await client.put(
        f"/api/v1/estacoes/{estacoes_seed[0].id}/cotas",
        json={
            "cota_atencao": "1.80",
            "cota_alerta": "2.40",
            "cota_emergencia": "3.10",
        },
        cookies=operador_cookies,
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_admin_acessa_rota_admin(
    client: AsyncClient,
    auth_cookies: dict[str, str],
    estacoes_seed: list[EstacaoMonitoramento],
) -> None:
    """Administrador autenticado tem acesso total a rotas admin (200)."""
    response = await client.put(
        f"/api/v1/estacoes/{estacoes_seed[0].id}/cotas",
        json={
            "cota_atencao": "1.80",
            "cota_alerta": "2.40",
            "cota_emergencia": "3.10",
        },
        cookies=auth_cookies,
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_token_invalido_ou_corrompido(client: AsyncClient) -> None:
    """Token de acesso com assinatura inválida deve retornar 401."""
    response = await client.post(
        "/api/v1/ocorrencias",
        json={},
        cookies={"access_token": "token-invalido-jwt"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Token expirado ou inválido."


@pytest.mark.asyncio
async def test_token_sem_sub(client: AsyncClient) -> None:
    """Token sem claim 'sub' deve retornar 401."""
    from jose import jwt

    from app.core.config import settings

    token = jwt.encode({"role": "ADMINISTRADOR"}, settings.JWT_SECRET_KEY, algorithm="HS256")
    response = await client.post(
        "/api/v1/ocorrencias",
        json={},
        cookies={"access_token": token},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Token inválido."


@pytest.mark.asyncio
async def test_token_sub_nao_uuid(client: AsyncClient) -> None:
    """Token com claim 'sub' que não é UUID deve retornar 401."""
    from jose import jwt

    from app.core.config import settings

    token = jwt.encode({"sub": "nao-eh-uuid"}, settings.JWT_SECRET_KEY, algorithm="HS256")
    response = await client.post(
        "/api/v1/ocorrencias",
        json={},
        cookies={"access_token": token},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Token inválido."


@pytest.mark.asyncio
async def test_usuario_inativo_rejeitado(
    client: AsyncClient, mock_db: "InMemoryAsyncSession"
) -> None:
    """Usuário com ativo=False deve ter acesso negado (401)."""
    from uuid import uuid4

    from app.core.security import create_access_token
    from app.models.usuario import PerfilUsuario

    user = Usuario(
        id=uuid4(),
        nome="Inativo",
        email="inativo@defesacivil.gov.br",
        senha_hash="hash",
        perfil=PerfilUsuario.OPERADOR_DEFESA_CIVIL,
        ativo=False,
    )
    mock_db.add(user)
    token = create_access_token({"sub": str(user.id), "role": user.perfil.value})
    response = await client.post(
        "/api/v1/ocorrencias",
        json={},
        cookies={"access_token": token},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Usuário não encontrado ou inativo."


@pytest.mark.asyncio
async def test_refresh_token_expirado_rejeitado(
    client: AsyncClient, usuario_seed: Usuario, mock_db: "InMemoryAsyncSession"
) -> None:
    """Refresh token expirado deve ser rejeitado com 401."""
    from datetime import UTC, datetime, timedelta
    from uuid import uuid4

    from app.core.security import create_refresh_token, hash_refresh_token
    from app.models.refresh_token import RefreshToken

    raw_token = create_refresh_token()
    token_db = RefreshToken(
        id=uuid4(),
        usuario_id=usuario_seed.id,
        token_hash=hash_refresh_token(raw_token),
        expira_em=datetime.now(UTC) - timedelta(days=1),  # Expirado
        revogado=False,
    )
    mock_db.add(token_db)
    response = await client.post(
        "/api/v1/auth/refresh",
        cookies={"refresh_token": raw_token},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Sessão inválida."
