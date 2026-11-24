"""Testes de integração para o registro operacional de ocorrências."""

import pytest
from httpx import AsyncClient
from sqlalchemy import text

from app.models.estacao import EstacaoMonitoramento
from tests.conftest import InMemoryAsyncSession


@pytest.mark.asyncio
async def test_criar_ocorrencia_como_operador(
    client: AsyncClient,
    operador_cookies: dict[str, str],
    estacoes_seed: list[EstacaoMonitoramento],
) -> None:
    """Operador da Defesa Civil pode registrar ocorrência de campo (201)."""
    response = await client.post(
        "/api/v1/ocorrencias",
        json={
            "estacao_id": str(estacoes_seed[0].id),
            "localizacao": "Rua das Flores, próximo à ponte",
            "descricao": "Nível do rio subindo rapidamente, moradores em alerta.",
        },
        cookies=operador_cookies,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "ABERTA"
    assert data["estacao_id"] == str(estacoes_seed[0].id)
    assert data["localizacao"] == "Rua das Flores, próximo à ponte"
    assert "criado_em" in data
    assert "id" in data


@pytest.mark.asyncio
async def test_criar_ocorrencia_como_admin(
    client: AsyncClient,
    admin_cookies: dict[str, str],
    estacoes_seed: list[EstacaoMonitoramento],
) -> None:
    """Administrador também possui permissão para registrar ocorrência (201)."""
    response = await client.post(
        "/api/v1/ocorrencias",
        json={
            "estacao_id": str(estacoes_seed[0].id),
            "localizacao": "Avenida Beira Rio, Centro",
            "descricao": "Vistoria preventiva concluída sem incidentes reportados.",
        },
        cookies=admin_cookies,
    )
    assert response.status_code == 201
    assert response.json()["status"] == "ABERTA"


@pytest.mark.asyncio
async def test_criar_ocorrencia_sem_autenticacao_retorna_401(
    client: AsyncClient,
    estacoes_seed: list[EstacaoMonitoramento],
) -> None:
    """Chamada não autenticada deve ser rejeitada com 401."""
    response = await client.post(
        "/api/v1/ocorrencias",
        json={
            "estacao_id": str(estacoes_seed[0].id),
            "localizacao": "Rua Qualquer, Bairro Central",
            "descricao": "Tentativa de registro sem credenciais válidas.",
        },
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_criar_ocorrencia_campos_invalidos_retorna_422(
    client: AsyncClient,
    operador_cookies: dict[str, str],
    estacoes_seed: list[EstacaoMonitoramento],
) -> None:
    """Campos que não atendem às restrições de tamanho são rejeitados com 422."""
    response = await client.post(
        "/api/v1/ocorrencias",
        json={
            "estacao_id": str(estacoes_seed[0].id),
            "localizacao": "Rua",  # Menor que 5 caracteres
            "descricao": "Curto",  # Menor que 10 caracteres
        },
        cookies=operador_cookies,
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_audit_log_registrado_apos_criar_ocorrencia(
    client: AsyncClient,
    operador_cookies: dict[str, str],
    estacoes_seed: list[EstacaoMonitoramento],
    db: InMemoryAsyncSession,
) -> None:
    """Criação de ocorrência gera registro correspondente na trilha de auditoria."""
    localizacao = "Ponte Velha do Paraíba"
    descricao = "Água atingiu cota de alerta na margem direita."
    await client.post(
        "/api/v1/ocorrencias",
        json={
            "estacao_id": str(estacoes_seed[0].id),
            "localizacao": localizacao,
            "descricao": descricao,
        },
        cookies=operador_cookies,
    )
    result = await db.execute(text("SELECT * FROM audit_log WHERE acao = 'CREATE_OCORRENCIA'"))
    logs = result.fetchall()
    assert len(logs) >= 1
    ultimo = logs[-1]
    assert ultimo.acao == "CREATE_OCORRENCIA"
    assert ultimo.dados_novos is not None
    assert ultimo.dados_novos["localizacao"] == localizacao
    assert ultimo.dados_novos["descricao"] == descricao


@pytest.mark.asyncio
async def test_listar_ocorrencias(
    client: AsyncClient,
    operador_cookies: dict[str, str],
    estacoes_seed: list[EstacaoMonitoramento],
) -> None:
    """Listagem de ocorrências retorna registros ordenados."""
    await client.post(
        "/api/v1/ocorrencias",
        json={
            "estacao_id": str(estacoes_seed[0].id),
            "localizacao": "Bairro Manejo, próximo à ponte",
            "descricao": "Nível da água subindo rapidamente, equipe a caminho.",
        },
        cookies=operador_cookies,
    )
    response = await client.get("/api/v1/ocorrencias")
    assert response.status_code == 200
    dados = response.json()
    assert isinstance(dados, list)
    assert len(dados) >= 1
    assert any(o["localizacao"] == "Bairro Manejo, próximo à ponte" for o in dados)


@pytest.mark.asyncio
async def test_atualizar_status_ocorrencia(
    client: AsyncClient,
    operador_cookies: dict[str, str],
    estacoes_seed: list[EstacaoMonitoramento],
) -> None:
    """Operador pode atualizar o status da ocorrência para EM_ANDAMENTO ou ENCERRADA."""
    post_res = await client.post(
        "/api/v1/ocorrencias",
        json={
            "estacao_id": str(estacoes_seed[0].id),
            "localizacao": "Campos Elíseos - Beira Rio",
            "descricao": "Infiltração de água na calçada da avenida Beira Rio.",
        },
        cookies=operador_cookies,
    )
    assert post_res.status_code == 201
    ocorrencia_id = post_res.json()["id"]

    patch_res = await client.patch(
        f"/api/v1/ocorrencias/{ocorrencia_id}/status",
        json={"status": "EM_ANDAMENTO"},
        cookies=operador_cookies,
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["status"] == "EM_ANDAMENTO"



@pytest.mark.asyncio
async def test_excluir_ocorrencia_registra_auditoria(
    client: AsyncClient,
    operador_cookies: dict[str, str],
    estacoes_seed: list[EstacaoMonitoramento],
    db: InMemoryAsyncSession,
) -> None:
    """Operador exclui a ocorrência (204) e o audit_log guarda os dados removidos."""
    criada = await client.post(
        "/api/v1/ocorrencias",
        json={
            "estacao_id": str(estacoes_seed[0].id),
            "localizacao": "Rua do Comércio, 120",
            "descricao": "Árvore caída obstruindo a via próxima ao rio.",
        },
        cookies=operador_cookies,
    )
    ocorrencia_id = criada.json()["id"]

    resposta = await client.delete(f"/api/v1/ocorrencias/{ocorrencia_id}", cookies=operador_cookies)
    assert resposta.status_code == 204
    assert db.ocorrencias == []
    assert any(log.acao == "DELETE_OCORRENCIA" for log in db.audit_logs)


@pytest.mark.asyncio
async def test_excluir_ocorrencia_inexistente_retorna_404(
    client: AsyncClient,
    operador_cookies: dict[str, str],
) -> None:
    resposta = await client.delete(
        "/api/v1/ocorrencias/00000000-0000-0000-0000-000000000000", cookies=operador_cookies
    )
    assert resposta.status_code == 404


@pytest.mark.asyncio
async def test_excluir_ocorrencia_sem_login_retorna_401(client: AsyncClient) -> None:
    resposta = await client.delete("/api/v1/ocorrencias/00000000-0000-0000-0000-000000000000")
    assert resposta.status_code == 401
