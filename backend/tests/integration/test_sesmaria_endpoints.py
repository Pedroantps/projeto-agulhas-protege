"""Testes de integração para os endpoints do Rio Sesmaria e IA."""

import pytest
from httpx import AsyncClient

from app.models.estacao import EstacaoMonitoramento


@pytest.mark.asyncio
async def test_get_sesmaria_dashboard_ia_sucesso(
    client: AsyncClient,
    estacoes_seed: list[EstacaoMonitoramento],
):
    response = await client.get("/api/v1/sesmaria/dashboard-ia")
    assert response.status_code == 200
    data = response.json()

    assert data["rio"] == "Rio Sesmaria"
    assert "telemetria" in data
    assert "correlacoes" in data
    assert len(data["correlacoes"]) >= 5
    assert "previsoes" in data
    assert len(data["previsoes"]) == 3
    assert "recomendacao_funil" in data
    assert "mensagem_alerta_whatsapp" in data


@pytest.mark.asyncio
async def test_get_sesmaria_alerta_whatsapp_sucesso(
    client: AsyncClient,
    estacoes_seed: list[EstacaoMonitoramento],
):
    response = await client.get("/api/v1/sesmaria/alerta-whatsapp")
    assert response.status_code == 200
    data = response.json()

    assert "mensagem" in data
    assert "url_whatsapp" in data
    assert data["url_whatsapp"].startswith("https://wa.me/?text=")
