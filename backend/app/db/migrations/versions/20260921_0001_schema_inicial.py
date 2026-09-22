"""Schema inicial da aplicação.

Revision ID: 20260921_0001
Revises:
Create Date: 2026-09-21
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260921_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

perfil_usuario = postgresql.ENUM(
    "ADMINISTRADOR",
    "OPERADOR_DEFESA_CIVIL",
    name="perfil_usuario",
    create_type=False,
)
nivel_risco_enum = postgresql.ENUM(
    "NORMAL",
    "ATENCAO",
    "ALERTA",
    "EMERGENCIA",
    name="nivel_risco_enum",
    create_type=False,
)
status_ocorrencia = postgresql.ENUM(
    "ABERTA",
    "EM_ANDAMENTO",
    "ENCERRADA",
    name="status_ocorrencia",
    create_type=False,
)


def upgrade() -> None:
    """Cria os ENUMs, tabelas e índices na ordem das dependências."""
    bind = op.get_bind()
    perfil_usuario.create(bind, checkfirst=True)
    nivel_risco_enum.create(bind, checkfirst=True)
    status_ocorrencia.create(bind, checkfirst=True)

    op.create_table(
        "usuarios",
        sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("nome", sa.String(length=150), nullable=False),
        sa.Column("email", sa.String(length=254), nullable=False),
        sa.Column("senha_hash", sa.Text(), nullable=False),
        sa.Column("perfil", perfil_usuario, nullable=False),
        sa.Column("ativo", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column(
            "criado_em", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "atualizado_em",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )

    op.create_table(
        "estacoes_monitoramento",
        sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("codigo_externo", sa.String(length=50), nullable=False),
        sa.Column("nome", sa.String(length=200), nullable=False),
        sa.Column("rio", sa.String(length=100), nullable=False),
        sa.Column("latitude", sa.Numeric(precision=9, scale=6), nullable=True),
        sa.Column("longitude", sa.Numeric(precision=9, scale=6), nullable=True),
        sa.Column("ativa", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column(
            "criado_em", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("codigo_externo"),
    )

    op.create_table(
        "niveis_risco",
        sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("estacao_id", sa.UUID(), nullable=False),
        sa.Column("cota_atencao", sa.Numeric(precision=6, scale=2), nullable=False),
        sa.Column("cota_alerta", sa.Numeric(precision=6, scale=2), nullable=False),
        sa.Column("cota_emergencia", sa.Numeric(precision=6, scale=2), nullable=False),
        sa.Column(
            "atualizado_em",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint(
            "cota_atencao < cota_alerta AND cota_alerta < cota_emergencia",
            name="cotas_ordem_crescente",
        ),
        sa.ForeignKeyConstraint(["estacao_id"], ["estacoes_monitoramento.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("estacao_id"),
    )

    op.create_table(
        "leituras_nivel",
        sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("estacao_id", sa.UUID(), nullable=False),
        sa.Column("data_hora", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("nivel_metros", sa.Numeric(precision=6, scale=3), nullable=False),
        sa.Column("classificacao", nivel_risco_enum, nullable=False),
        sa.Column("fonte", sa.String(length=100), nullable=True),
        sa.Column(
            "criado_em", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["estacao_id"], ["estacoes_monitoramento.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "idx_leituras_estacao_data",
        "leituras_nivel",
        ["estacao_id", sa.desc("data_hora")],
    )

    op.create_table(
        "alertas",
        sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("estacao_id", sa.UUID(), nullable=False),
        sa.Column("leitura_id", sa.UUID(), nullable=False),
        sa.Column("nivel_risco", nivel_risco_enum, nullable=False),
        sa.Column("encerrado_por", sa.UUID(), nullable=True),
        sa.Column(
            "criado_em", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("encerrado_em", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["encerrado_por"], ["usuarios.id"]),
        sa.ForeignKeyConstraint(["estacao_id"], ["estacoes_monitoramento.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["leitura_id"], ["leituras_nivel.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "idx_alertas_ativos",
        "alertas",
        ["estacao_id"],
        postgresql_where=sa.text("encerrado_em IS NULL"),
    )

    op.create_table(
        "ocorrencias",
        sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("usuario_id", sa.UUID(), nullable=False),
        sa.Column("estacao_id", sa.UUID(), nullable=False),
        sa.Column("alerta_id", sa.UUID(), nullable=True),
        sa.Column("localizacao", sa.String(length=300), nullable=False),
        sa.Column("descricao", sa.Text(), nullable=False),
        sa.Column("status", status_ocorrencia, server_default=sa.text("'ABERTA'"), nullable=False),
        sa.Column(
            "criado_em", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "atualizado_em",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["alerta_id"], ["alertas.id"]),
        sa.ForeignKeyConstraint(["estacao_id"], ["estacoes_monitoramento.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "refresh_tokens",
        sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("usuario_id", sa.UUID(), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("expira_em", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("revogado", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column(
            "criado_em", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token_hash"),
    )
    op.create_index(
        "idx_refresh_tokens_usuario",
        "refresh_tokens",
        ["usuario_id"],
        postgresql_where=sa.text("NOT revogado"),
    )

    op.create_table(
        "audit_log",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("usuario_id", sa.UUID(), nullable=True),
        sa.Column("acao", sa.String(length=50), nullable=False),
        sa.Column("entidade", sa.String(length=100), nullable=False),
        sa.Column("entidade_id", sa.UUID(), nullable=False),
        sa.Column("dados_anteriores", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("dados_novos", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("ip_address", postgresql.INET(), nullable=True),
        sa.Column("request_id", sa.String(length=36), nullable=True),
        sa.Column(
            "criado_em", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "idx_audit_log_entidade",
        "audit_log",
        ["entidade", "entidade_id", sa.desc("criado_em")],
    )
    op.create_index("idx_audit_log_usuario", "audit_log", ["usuario_id", sa.desc("criado_em")])


def downgrade() -> None:
    """Remove o schema em ordem inversa às chaves estrangeiras."""
    op.drop_index("idx_audit_log_usuario", table_name="audit_log")
    op.drop_index("idx_audit_log_entidade", table_name="audit_log")
    op.drop_table("audit_log")
    op.drop_index("idx_refresh_tokens_usuario", table_name="refresh_tokens")
    op.drop_table("refresh_tokens")
    op.drop_table("ocorrencias")
    op.drop_index("idx_alertas_ativos", table_name="alertas")
    op.drop_table("alertas")
    op.drop_index("idx_leituras_estacao_data", table_name="leituras_nivel")
    op.drop_table("leituras_nivel")
    op.drop_table("niveis_risco")
    op.drop_table("estacoes_monitoramento")
    op.drop_table("usuarios")

    bind = op.get_bind()
    status_ocorrencia.drop(bind, checkfirst=True)
    nivel_risco_enum.drop(bind, checkfirst=True)
    perfil_usuario.drop(bind, checkfirst=True)
