"""Schemas para registro e consulta de ocorrências operacionais."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_validator


class CriarOcorrenciaRequest(BaseModel):
    """Schema de entrada para criação de ocorrência de campo.

    Proteção estrita contra mass assignment:
    nenhum campo de sistema (usuario_id, status, criado_em) é aceito pelo cliente.
    """

    model_config = ConfigDict(extra="forbid")

    estacao_id: UUID
    alerta_id: UUID | None = None
    localizacao: str
    descricao: str

    @field_validator("localizacao")
    @classmethod
    def localizacao_nao_vazia(cls, v: str) -> str:
        """Valida tamanho mínimo da localização."""
        v_stripped = v.strip()
        if len(v_stripped) < 5:
            msg = "Localização deve ter pelo menos 5 caracteres."
            raise ValueError(msg)
        return v_stripped

    @field_validator("descricao")
    @classmethod
    def descricao_nao_vazia(cls, v: str) -> str:
        """Valida tamanho mínimo da descrição."""
        v_stripped = v.strip()
        if len(v_stripped) < 10:
            msg = "Descrição deve ter pelo menos 10 caracteres."
            raise ValueError(msg)
        return v_stripped


class OcorrenciaResponse(BaseModel):
    """Dados retornados após o registro ou listagem de uma ocorrência."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    estacao_id: UUID
    estacao_nome: str | None = None
    usuario_nome: str | None = None
    alerta_id: UUID | None = None
    localizacao: str
    descricao: str
    status: str
    criado_em: datetime
    atualizado_em: datetime | None = None


class AtualizarStatusOcorrenciaRequest(BaseModel):
    """Schema para atualização do status de atendimento da ocorrência."""

    model_config = ConfigDict(extra="forbid")

    status: str

