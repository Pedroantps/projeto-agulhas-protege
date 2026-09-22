"""Schemas para estações e consulta de status atual."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class CotasSchema(BaseModel):
    """Limiares de cota associados a uma estação."""

    model_config = ConfigDict(extra="forbid")

    atencao: Decimal
    alerta: Decimal
    emergencia: Decimal


class StatusAtualResponse(BaseModel):
    """Status hidrológico atual de uma estação com última leitura."""

    model_config = ConfigDict(from_attributes=True)

    estacao_id: str
    codigo_externo: str
    nome: str
    rio: str
    nivel_atual_metros: Decimal
    classificacao_risco: str
    data_hora_leitura: datetime
    dados_desatualizados: bool
    cotas: CotasSchema
