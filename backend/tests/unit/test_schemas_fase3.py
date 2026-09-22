"""Testes unitários dos schemas Pydantic da Fase 3."""

from decimal import Decimal
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.schemas.cotas import AtualizarCotasRequest
from app.schemas.leitura import HistoricoQuery
from app.schemas.ocorrencia import CriarOcorrenciaRequest


def test_cotas_validas() -> None:
    """Cotas estritamente crescentes e positivas são aceitas."""
    req = AtualizarCotasRequest(
        cota_atencao=Decimal("1.80"),
        cota_alerta=Decimal("2.40"),
        cota_emergencia=Decimal("3.10"),
    )
    assert req.cota_atencao == Decimal("1.80")
    assert req.cota_alerta == Decimal("2.40")
    assert req.cota_emergencia == Decimal("3.10")


def test_cotas_zero_ou_negativa_rejeitada() -> None:
    """Cotas menores ou iguais a zero devem levantar ValidationError."""
    with pytest.raises(ValidationError, match="Cotas devem ser positivas"):
        AtualizarCotasRequest(
            cota_atencao=Decimal("0.00"),
            cota_alerta=Decimal("2.00"),
            cota_emergencia=Decimal("3.00"),
        )

    with pytest.raises(ValidationError, match="Cotas devem ser positivas"):
        AtualizarCotasRequest(
            cota_atencao=Decimal("-1.00"),
            cota_alerta=Decimal("2.00"),
            cota_emergencia=Decimal("3.00"),
        )


def test_cotas_ordem_invalida_rejeitada() -> None:
    """Ordem não crescente deve levantar ValidationError."""
    # alerta <= atencao
    with pytest.raises(ValidationError, match="As cotas devem ser crescentes"):
        AtualizarCotasRequest(
            cota_atencao=Decimal("2.50"),
            cota_alerta=Decimal("2.00"),
            cota_emergencia=Decimal("3.00"),
        )

    # alerta == atencao
    with pytest.raises(ValidationError, match="As cotas devem ser crescentes"):
        AtualizarCotasRequest(
            cota_atencao=Decimal("2.00"),
            cota_alerta=Decimal("2.00"),
            cota_emergencia=Decimal("3.00"),
        )

    # emergencia <= alerta
    with pytest.raises(ValidationError, match="As cotas devem ser crescentes"):
        AtualizarCotasRequest(
            cota_atencao=Decimal("1.50"),
            cota_alerta=Decimal("2.50"),
            cota_emergencia=Decimal("2.40"),
        )


def test_ocorrencia_validacoes_string() -> None:
    """Valida requisitos de tamanho e strip para campos de ocorrência."""
    estacao_id = uuid4()
    req = CriarOcorrenciaRequest(
        estacao_id=estacao_id,
        localizacao="   Rua das Palmeiras, 100   ",
        descricao="   Nível da água subindo rapidamente perto do bueiro.   ",
    )
    assert req.localizacao == "Rua das Palmeiras, 100"
    assert req.descricao == "Nível da água subindo rapidamente perto do bueiro."

    # Localização muito curta
    with pytest.raises(ValidationError, match="Localização deve ter pelo menos 5 caracteres"):
        CriarOcorrenciaRequest(
            estacao_id=estacao_id,
            localizacao="  Rua ",
            descricao="Descrição válida com mais de dez caracteres",
        )

    # Descrição muito curta
    with pytest.raises(ValidationError, match="Descrição deve ter pelo menos 10 caracteres"):
        CriarOcorrenciaRequest(
            estacao_id=estacao_id,
            localizacao="Localização Válida",
            descricao="Curta",
        )


def test_historico_query_validacao_horas() -> None:
    """Valida intervalo de horas permitido para histórico."""
    estacao_id = uuid4()
    # Válido
    q = HistoricoQuery(estacao_id=estacao_id, horas=24)
    assert q.horas == 24

    # Limite máximo de 90 dias (2160h)
    q_max = HistoricoQuery(estacao_id=estacao_id, horas=2160)
    assert q_max.horas == 2160

    # Menor que 1
    with pytest.raises(ValidationError, match="Período deve estar entre 1 hora e 2160 horas"):
        HistoricoQuery(estacao_id=estacao_id, horas=0)

    # Maior que 2160
    with pytest.raises(ValidationError, match="Período deve estar entre 1 hora e 2160 horas"):
        HistoricoQuery(estacao_id=estacao_id, horas=2161)
