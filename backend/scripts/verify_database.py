"""Verifica automaticamente os critérios de conclusão da Fase 1."""

import asyncio
import sys
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.db.session import AsyncSessionLocal  # noqa: E402

EXPECTED_TABLES = {
    "usuarios",
    "estacoes_monitoramento",
    "niveis_risco",
    "leituras_nivel",
    "alertas",
    "ocorrencias",
    "refresh_tokens",
    "audit_log",
}


async def verify_database() -> None:
    """Valida tabelas, seed, constraint e índice no PostgreSQL configurado."""
    async with AsyncSessionLocal() as db:
        table_names = set(
            await db.scalars(
                text(
                    """
                    SELECT tablename
                    FROM pg_catalog.pg_tables
                    WHERE schemaname = current_schema()
                    """
                )
            )
        )
        missing_tables = EXPECTED_TABLES - table_names
        if missing_tables:
            message = f"Tabelas ausentes: {sorted(missing_tables)}"
            raise AssertionError(message)

        seed_counts = (
            await db.execute(
                text(
                    """
                    SELECT
                        (SELECT COUNT(*) FROM usuarios
                         WHERE email IN (
                            'admin@defesacivil.resende.rj.gov.br',
                            'operador@defesacivil.resende.rj.gov.br'
                         )),
                        (SELECT COUNT(*) FROM estacoes_monitoramento
                         WHERE codigo_externo = 'SESMARIA-01'),
                        (SELECT COUNT(*) FROM niveis_risco nr
                         JOIN estacoes_monitoramento e ON e.id = nr.estacao_id
                         WHERE e.codigo_externo = 'SESMARIA-01')
                    """
                )
            )
        ).one()
        if seed_counts != (2, 1, 1):
            message = f"Seed incompleto (usuários, estações, cotas): {seed_counts}"
            raise AssertionError(message)

        index_exists = await db.scalar(
            text(
                """
                SELECT EXISTS (
                    SELECT 1 FROM pg_indexes
                    WHERE schemaname = current_schema()
                      AND indexname = 'idx_leituras_estacao_data'
                )
                """
            )
        )
        if not index_exists:
            raise AssertionError("Índice idx_leituras_estacao_data ausente.")

        try:
            async with db.begin_nested():
                estacao_id = await db.scalar(
                    text(
                        """
                        INSERT INTO estacoes_monitoramento (codigo_externo, nome, rio)
                        VALUES (
                            'V-CONST-' || gen_random_uuid(),
                            'Temporária',
                            'Rio Teste'
                        )
                        RETURNING id
                        """
                    )
                )
                await db.execute(
                    text(
                        """
                        INSERT INTO niveis_risco (
                            estacao_id, cota_atencao, cota_alerta, cota_emergencia
                        ) VALUES (:estacao_id, 3.00, 2.00, 4.00)
                        """
                    ),
                    {"estacao_id": estacao_id},
                )
        except IntegrityError:
            pass
        else:
            raise AssertionError("A constraint cotas_ordem_crescente não rejeitou cotas inválidas.")

    print("Banco da Fase 1 validado com sucesso.")


if __name__ == "__main__":
    asyncio.run(verify_database())
