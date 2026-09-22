"""Testes de integração para a série histórica de leituras de nível."""

from uuid import uuid4

import pytest
from httpx import AsyncClient

from app.models.estacao import EstacaoMonitoramento


@pytest.mark.asyncio
async def test_historico_publico(
    client: AsyncClient, estacoes_seed: list[EstacaoMonitoramento]
) -> None:
    """Endpoint público /historico retorna pontos cronológicos."""
    response = await client.get(
        "/api/v1/leituras/historico",
        params={"estacao_id": str(estacoes_seed[0].id), "horas": 24},
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    ponto = data[0]
    assert "id" in ponto
    assert "data_hora" in ponto
    assert "nivel_metros" in ponto
    assert "classificacao" in ponto


@pytest.mark.asyncio
async def test_historico_periodo_invalido_retorna_422(
    client: AsyncClient, estacoes_seed: list[EstacaoMonitoramento]
) -> None:
    """Período fora dos limites (1 a 2160 horas) deve retornar 422."""
    # Maior que 90 dias (2160h)
    resp_max = await client.get(
        "/api/v1/leituras/historico",
        params={"estacao_id": str(estacoes_seed[0].id), "horas": 9999},
    )
    assert resp_max.status_code == 422

    # Menor que 1 hora
    resp_min = await client.get(
        "/api/v1/leituras/historico",
        params={"estacao_id": str(estacoes_seed[0].id), "horas": 0},
    )
    assert resp_min.status_code == 422


@pytest.mark.asyncio
async def test_historico_estacao_inexistente_retorna_404(client: AsyncClient) -> None:
    """Consulta para estação inexistente retorna 404."""
    id_aleatorio = uuid4()
    response = await client.get(
        "/api/v1/leituras/historico",
        params={"estacao_id": str(id_aleatorio), "horas": 24},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_historico_estacao_uuid_invalido_retorna_422(client: AsyncClient) -> None:
    """Parâmetro estacao_id que não é UUID deve retornar 422."""
    response = await client.get(
        "/api/v1/leituras/historico",
        params={"estacao_id": "uuid-invalido", "horas": 24},
    )
    assert response.status_code == 422
