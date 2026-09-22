"""Testes de validação do schema de cotas."""

from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.schemas.cotas import AtualizarCotasRequest


def test_cotas_validas() -> None:
    cotas = AtualizarCotasRequest(
        cota_atencao=Decimal("2.00"),
        cota_alerta=Decimal("2.50"),
        cota_emergencia=Decimal("3.20"),
    )
    assert cotas.cota_atencao < cotas.cota_alerta < cotas.cota_emergencia


@pytest.mark.parametrize(
    ("atencao", "alerta", "emergencia"),
    [
        (Decimal("2.50"), Decimal("2.00"), Decimal("3.20")),  # alerta < atencao
        (Decimal("2.00"), Decimal("3.20"), Decimal("3.20")),  # alerta == emergencia
        (Decimal("3.20"), Decimal("2.50"), Decimal("2.00")),  # ordem totalmente inversa
        (Decimal("-1.00"), Decimal("2.00"), Decimal("3.00")),  # atencao negativa
    ],
)
def test_cotas_invalidas_levantam_validation_error(
    atencao: Decimal, alerta: Decimal, emergencia: Decimal
) -> None:
    with pytest.raises(ValidationError):
        AtualizarCotasRequest(
            cota_atencao=atencao,
            cota_alerta=alerta,
            cota_emergencia=emergencia,
        )
