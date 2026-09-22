"""Schemas para consultas e respostas de leituras históricas."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_validator


class HistoricoQuery(BaseModel):
    """Parâmetros de consulta do histórico de leituras."""

    model_config = ConfigDict(extra="forbid")

    estacao_id: UUID
    horas: int = 24

    @field_validator("horas")
    @classmethod
    def horas_validas(cls, v: int) -> int:
        """Garante período entre 1 hora e 2160 horas (90 dias)."""
        if v < 1 or v > 2160:
            msg = "Período deve estar entre 1 hora e 2160 horas (90 dias)."
            raise ValueError(msg)
        return v


class LeituraHistoricoResponse(BaseModel):
    """Ponto temporal de leitura do nível do rio."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    data_hora: datetime
    nivel_metros: Decimal
    classificacao: str
