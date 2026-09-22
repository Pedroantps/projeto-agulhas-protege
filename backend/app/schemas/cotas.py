"""Schemas de validação para cotas hidrológicas de risco."""

from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, model_validator


class AtualizarCotasRequest(BaseModel):
    """Schema de validação para alteração de cotas de risco.

    Usa Decimal para evitar imprecisões de ponto flutuante e extra='forbid'
    para prevenir injeção de parâmetros não permitidos.
    """

    model_config = ConfigDict(extra="forbid")

    cota_atencao: Decimal
    cota_alerta: Decimal
    cota_emergencia: Decimal

    @model_validator(mode="after")
    def validar_ordem_crescente(self) -> "AtualizarCotasRequest":
        """Garante cotas positivas e estritamente crescentes."""
        if self.cota_atencao <= Decimal("0"):
            msg = "Cotas devem ser positivas."
            raise ValueError(msg)
        if not (self.cota_atencao < self.cota_alerta < self.cota_emergencia):
            msg = "As cotas devem ser crescentes: atenção < alerta < emergência."
            raise ValueError(msg)
        return self


class CotasResponse(BaseModel):
    """Schema de resposta após atualização de cotas."""

    model_config = ConfigDict(from_attributes=True)

    estacao_id: UUID
    cota_atencao: Decimal
    cota_alerta: Decimal
    cota_emergencia: Decimal
