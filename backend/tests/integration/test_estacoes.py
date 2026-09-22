"""Testes de integração para os endpoints de estações e cotas."""

from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy import text

from app.models.estacao import EstacaoMonitoramento
from tests.conftest import InMemoryAsyncSession


@pytest.mark.asyncio
async def test_status_atual_publico(
    client: AsyncClient, estacoes_seed: list[EstacaoMonitoramento]
) -> None:
    """Endpoint público /status-atual não requer autenticação e retorna status calculado."""
    response = await client.get("/api/v1/estacoes/status-atual")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    primeira = data[0]
    assert primeira["estacao_id"] == str(estacoes_seed[0].id)
    assert "nivel_atual_metros" in primeira
    assert "classificacao_risco" in primeira
    assert "dados_desatualizados" in primeira
    assert "cotas" in primeira
    assert "atencao" in primeira["cotas"]
    assert "alerta" in primeira["cotas"]
    assert "emergencia" in primeira["cotas"]


@pytest.mark.asyncio
async def test_atualizar_cotas_como_admin(
    client: AsyncClient,
    admin_cookies: dict[str, str],
    estacoes_seed: list[EstacaoMonitoramento],
) -> None:
    """Administrador autenticado pode atualizar cotas de risco."""
    response = await client.put(
        f"/api/v1/estacoes/{estacoes_seed[0].id}/cotas",
        json={
            "cota_atencao": "1.80",
            "cota_alerta": "2.40",
            "cota_emergencia": "3.10",
        },
        cookies=admin_cookies,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["estacao_id"] == str(estacoes_seed[0].id)
    assert data["cota_atencao"] == "1.80"
    assert data["cota_alerta"] == "2.40"
    assert data["cota_emergencia"] == "3.10"


@pytest.mark.asyncio
async def test_atualizar_cotas_como_operador_retorna_403(
    client: AsyncClient,
    operador_cookies: dict[str, str],
    estacoes_seed: list[EstacaoMonitoramento],
) -> None:
    """Operador não tem permissão para alterar cotas de risco (403)."""
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
async def test_atualizar_cotas_sem_auth_retorna_401(
    client: AsyncClient, estacoes_seed: list[EstacaoMonitoramento]
) -> None:
    """Tentativa anônima de alterar cotas deve retornar 401."""
    response = await client.put(
        f"/api/v1/estacoes/{estacoes_seed[0].id}/cotas",
        json={
            "cota_atencao": "1.80",
            "cota_alerta": "2.40",
            "cota_emergencia": "3.10",
        },
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_atualizar_cotas_estacao_inexistente_retorna_404(
    client: AsyncClient, admin_cookies: dict[str, str]
) -> None:
    """Atualização em estação não cadastrada retorna 404."""
    id_aleatorio = uuid4()
    response = await client.put(
        f"/api/v1/estacoes/{id_aleatorio}/cotas",
        json={
            "cota_atencao": "1.80",
            "cota_alerta": "2.40",
            "cota_emergencia": "3.10",
        },
        cookies=admin_cookies,
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_cotas_ordem_invalida_retorna_422(
    client: AsyncClient,
    admin_cookies: dict[str, str],
    estacoes_seed: list[EstacaoMonitoramento],
) -> None:
    """Cotas com ordem decrescente ou incoerente são rejeitadas com 422."""
    response = await client.put(
        f"/api/v1/estacoes/{estacoes_seed[0].id}/cotas",
        json={
            "cota_atencao": "3.00",
            "cota_alerta": "2.00",
            "cota_emergencia": "4.00",
        },
        cookies=admin_cookies,
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_audit_log_registrado_apos_update_cotas(
    client: AsyncClient,
    admin_cookies: dict[str, str],
    estacoes_seed: list[EstacaoMonitoramento],
    db: InMemoryAsyncSession,
) -> None:
    """Alteração de cotas gera registro correspondente na trilha de auditoria."""
    await client.put(
        f"/api/v1/estacoes/{estacoes_seed[0].id}/cotas",
        json={
            "cota_atencao": "2.10",
            "cota_alerta": "2.60",
            "cota_emergencia": "3.30",
        },
        cookies=admin_cookies,
    )
    result = await db.execute(text("SELECT * FROM audit_log WHERE acao = 'UPDATE_COTAS'"))
    logs = result.fetchall()
    assert len(logs) >= 1
    ultimo = logs[-1]
    assert ultimo.acao == "UPDATE_COTAS"
    assert ultimo.dados_anteriores is not None
    assert ultimo.dados_novos is not None
    assert ultimo.dados_novos["cota_atencao"] == "2.10"


# ── Nomes explícitos conforme especificação da Fase 6.4 ───────────────────

test_status_atual_retorna_200_sem_autenticacao = test_status_atual_publico
test_atualizar_cotas_admin_sucesso = test_atualizar_cotas_como_admin
test_atualizar_cotas_operador_retorna_403 = test_atualizar_cotas_como_operador_retorna_403
test_cotas_fora_de_ordem_retorna_422 = test_cotas_ordem_invalida_retorna_422


@pytest.mark.asyncio
async def test_historico_rejeita_periodo_acima_do_maximo(client: AsyncClient) -> None:
    """Verifica rejeição de período histórico além do limite máximo com 422."""
    response = await client.get(
        "/api/v1/leituras/historico",
        params={"estacao_id": "00000000-0000-0000-0000-000000000000", "horas": 9999},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_criar_ocorrencia_operador_sucesso(
    client: AsyncClient, operador_cookies: dict[str, str], estacoes_seed: list[EstacaoMonitoramento]
) -> None:
    """Registro de ocorrência por operador autenticado retorna 201."""
    response = await client.post(
        "/api/v1/ocorrencias",
        json={
            "estacao_id": str(estacoes_seed[0].id),
            "localizacao": "Rua das Flores, 123 — próximo à ponte",
            "descricao": "Nível subindo rapidamente, vizinhos saindo de casa.",
        },
        cookies=operador_cookies,
    )
    assert response.status_code == 201
    assert response.json()["status"] == "ABERTA"


@pytest.mark.asyncio
async def test_criar_ocorrencia_sem_autenticacao_retorna_401(
    client: AsyncClient, estacoes_seed: list[EstacaoMonitoramento]
) -> None:
    """Tentativa de criar ocorrência sem autenticação retorna 401."""
    response = await client.post(
        "/api/v1/ocorrencias",
        json={
            "estacao_id": str(estacoes_seed[0].id),
            "localizacao": "Algum lugar",
            "descricao": "Situação crítica observada.",
        },
    )
    assert response.status_code == 401
