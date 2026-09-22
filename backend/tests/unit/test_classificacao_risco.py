"""Testes unitários do motor de classificação de risco hidrológico."""

from decimal import Decimal

import pytest

from app.models.leitura import NivelRiscoEnum
from app.schemas.estacao import CotasSchema
from app.services.classificacao_risco import classificar_risco


@pytest.mark.parametrize(
    ("nivel", "esperado"),
    [
        (Decimal("1.50"), NivelRiscoEnum.NORMAL),
        (Decimal("1.99"), NivelRiscoEnum.NORMAL),
        (Decimal("2.00"), NivelRiscoEnum.ATENCAO),
        (Decimal("2.49"), NivelRiscoEnum.ATENCAO),
        (Decimal("2.50"), NivelRiscoEnum.ALERTA),
        (Decimal("3.19"), NivelRiscoEnum.ALERTA),
        (Decimal("3.20"), NivelRiscoEnum.EMERGENCIA),
        (Decimal("5.00"), NivelRiscoEnum.EMERGENCIA),
    ],
)
def test_classificar_risco_parametrizado(nivel: Decimal, esperado: NivelRiscoEnum) -> None:
    """Testa os 4 níveis de risco com valores de fronteira."""
    cotas = CotasSchema(
        atencao=Decimal("2.00"),
        alerta=Decimal("2.50"),
        emergencia=Decimal("3.20"),
    )
    assert classificar_risco(nivel, cotas) == esperado


def test_classificar_risco_usa_decimal_nao_float() -> None:
    """Garante que o motor aceita Decimal, não float."""
    cotas = CotasSchema(
        atencao=Decimal("2.00"),
        alerta=Decimal("2.50"),
        emergencia=Decimal("3.20"),
    )
    nivel = Decimal("2.4999999999")  # Limite inferior de ATENCAO
    resultado = classificar_risco(nivel, cotas)
    assert resultado == NivelRiscoEnum.ATENCAO
