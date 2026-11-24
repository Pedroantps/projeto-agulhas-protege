"""Coleta de dados reais: unicidade das leituras e instantâneos da bacia.

Revision ID: 20261123_0002
Revises: 20260921_0001
Create Date: 2026-11-23
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20261123_0002"
down_revision: str | None = "20260921_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Impede leituras duplicadas e cria a tabela de instantâneos da bacia."""
    # Remove duplicatas eventuais antes de criar a restrição de unicidade.
    op.execute(
        """
        DELETE FROM leituras_nivel a USING leituras_nivel b
        WHERE a.estacao_id = b.estacao_id AND a.data_hora = b.data_hora AND a.id > b.id
          AND NOT EXISTS (SELECT 1 FROM alertas al WHERE al.leitura_id = a.id)
        """
    )
    op.create_unique_constraint(
        "uq_leituras_estacao_data_hora", "leituras_nivel", ["estacao_id", "data_hora"]
    )
    op.create_table(
        "coletas_bacia",
        sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column(
            "coletado_em", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("payload", postgresql.JSONB(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_coletas_bacia_coletado_em", "coletas_bacia", ["coletado_em"])


def downgrade() -> None:
    """Reverte as alterações."""
    op.drop_index("ix_coletas_bacia_coletado_em", table_name="coletas_bacia")
    op.drop_table("coletas_bacia")
    op.drop_constraint("uq_leituras_estacao_data_hora", "leituras_nivel", type_="unique")
