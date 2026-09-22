"""Testes do endpoint de saúde e middleware stack."""

from httpx import AsyncClient


async def test_health_check(client: AsyncClient) -> None:
    """O health check expõe status, versão e cabeçalhos defensivos."""
    response = await client.get("/health", headers={"X-Request-ID": "test-request-id"})

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "versao": "1.0.0"}
    assert response.headers["x-request-id"] == "test-request-id"
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
