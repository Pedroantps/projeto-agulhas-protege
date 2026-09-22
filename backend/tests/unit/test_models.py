"""Testes estruturais do schema ORM da fase 1."""

from typing import cast

from sqlalchemy import CheckConstraint, Table

from app.db.base import Base
from app.models import Alerta, LeituraNivel, NivelRisco, RefreshToken


def test_metadata_contem_as_oito_tabelas_da_fase() -> None:
    assert set(Base.metadata.tables) == {
        "usuarios",
        "estacoes_monitoramento",
        "niveis_risco",
        "leituras_nivel",
        "alertas",
        "ocorrencias",
        "refresh_tokens",
        "audit_log",
    }


def test_constraint_de_cotas_esta_registrada() -> None:
    table = cast(Table, NivelRisco.__table__)
    constraints = {
        constraint.name
        for constraint in table.constraints
        if isinstance(constraint, CheckConstraint)
    }
    assert "cotas_ordem_crescente" in constraints


def test_indices_criticos_estao_registrados() -> None:
    leitura_tbl = cast(Table, LeituraNivel.__table__)
    alerta_tbl = cast(Table, Alerta.__table__)
    refresh_tbl = cast(Table, RefreshToken.__table__)
    assert "idx_leituras_estacao_data" in {index.name for index in leitura_tbl.indexes}
    assert "idx_alertas_ativos" in {index.name for index in alerta_tbl.indexes}
    assert "idx_refresh_tokens_usuario" in {index.name for index in refresh_tbl.indexes}
