"""Popula o banco com os dados mínimos do ambiente de desenvolvimento."""

import asyncio
import sys
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.security import hash_password  # noqa: E402
from app.db.session import AsyncSessionLocal  # noqa: E402
from app.models.estacao import EstacaoMonitoramento  # noqa: E402
from app.models.leitura import LeituraNivel  # noqa: E402
from app.models.niveis_risco import NivelRisco  # noqa: E402
from app.models.usuario import PerfilUsuario, Usuario  # noqa: E402
from app.schemas.estacao import CotasSchema  # noqa: E402
from app.services.classificacao_risco import classificar_risco  # noqa: E402


async def _upsert_usuario(
    db: AsyncSession,
    *,
    nome: str,
    email: str,
    password: str,
    perfil: PerfilUsuario,
) -> Usuario:
    usuario = await db.scalar(select(Usuario).where(Usuario.email == email))
    if usuario is None:
        usuario = Usuario(
            nome=nome,
            email=email,
            senha_hash=hash_password(password),
            perfil=perfil,
        )
        db.add(usuario)
    else:
        usuario.nome = nome
        usuario.perfil = perfil
        usuario.ativo = True
    return usuario


async def _upsert_estacao(
    db: AsyncSession,
    *,
    codigo_externo: str,
    nome: str,
    rio: str,
    latitude: Decimal,
    longitude: Decimal,
) -> EstacaoMonitoramento:
    estacao = await db.scalar(
        select(EstacaoMonitoramento).where(EstacaoMonitoramento.codigo_externo == codigo_externo)
    )
    if estacao is None:
        estacao = EstacaoMonitoramento(
            codigo_externo=codigo_externo,
            nome=nome,
            rio=rio,
            latitude=latitude,
            longitude=longitude,
        )
        db.add(estacao)
    else:
        estacao.nome = nome
        estacao.rio = rio
        estacao.latitude = latitude
        estacao.longitude = longitude
        estacao.ativa = True
    await db.flush()
    return estacao


async def _upsert_cotas(
    db: AsyncSession,
    *,
    estacao: EstacaoMonitoramento,
    atencao: Decimal,
    alerta: Decimal,
    emergencia: Decimal,
) -> None:
    cotas = await db.scalar(select(NivelRisco).where(NivelRisco.estacao_id == estacao.id))
    if cotas is None:
        db.add(
            NivelRisco(
                estacao_id=estacao.id,
                cota_atencao=atencao,
                cota_alerta=alerta,
                cota_emergencia=emergencia,
            )
        )
        return
    cotas.cota_atencao = atencao
    cotas.cota_alerta = alerta
    cotas.cota_emergencia = emergencia


async def _seed_leituras(
    db: AsyncSession,
    *,
    estacao: EstacaoMonitoramento,
    cotas: dict[str, Decimal],
    leituras_base: list[tuple[int, Decimal]],
) -> None:
    count = await db.scalar(
        select(func.count(LeituraNivel.id)).where(LeituraNivel.estacao_id == estacao.id)
    )
    if count and count > 0:
        return

    now = datetime.now(UTC)
    schema_cotas = CotasSchema(
        atencao=cotas["atencao"],
        alerta=cotas["alerta"],
        emergencia=cotas["emergencia"],
    )
    for horas_atras, nivel in leituras_base:
        data_hora = now - timedelta(hours=horas_atras)
        classificacao = classificar_risco(nivel, schema_cotas)
        db.add(
            LeituraNivel(
                estacao_id=estacao.id,
                data_hora=data_hora,
                nivel_metros=nivel,
                classificacao=classificacao,
                fonte="SIMULADOR_TELEMETRIA",
            )
        )


async def seed() -> None:
    """Insere ou atualiza usuários, estações, cotas e leituras conhecidas."""
    async with AsyncSessionLocal() as db:
        async with db.begin():
            await _upsert_usuario(
                db,
                nome="Administrador Padrão",
                email="admin@defesacivil.resende.rj.gov.br",
                password="Admin@2026",  # noqa: S106 - credencial exclusiva do seed local
                perfil=PerfilUsuario.ADMINISTRADOR,
            )
            await _upsert_usuario(
                db,
                nome="Operador Plantão A",
                email="operador@defesacivil.resende.rj.gov.br",
                password="Operador@2026",  # noqa: S106 - credencial exclusiva do seed local
                perfil=PerfilUsuario.OPERADOR_DEFESA_CIVIL,
            )

            estacao_sesmaria = await _upsert_estacao(
                db,
                codigo_externo="SESMARIA-01",
                nome="Estação Parque Ipiranga",
                rio="Rio Sesmaria",
                latitude=Decimal("-22.4653"),
                longitude=Decimal("-44.4503"),
            )

            # Limpeza preventiva: remove qualquer estação mockada antiga (como Alambari)
            estacao_legada = await db.scalar(
                select(EstacaoMonitoramento).where(EstacaoMonitoramento.codigo_externo == "ALAMBARI-01")
            )
            if estacao_legada is not None:
                await db.execute(
                    delete(LeituraNivel).where(LeituraNivel.estacao_id == estacao_legada.id)
                )
                await db.execute(
                    delete(NivelRisco).where(NivelRisco.estacao_id == estacao_legada.id)
                )
                await db.execute(
                    delete(EstacaoMonitoramento).where(EstacaoMonitoramento.id == estacao_legada.id)
                )

            await _upsert_cotas(
                db,
                estacao=estacao_sesmaria,
                atencao=Decimal("2.00"),
                alerta=Decimal("2.50"),
                emergencia=Decimal("3.20"),
            )

            # Leituras simuladas do Rio Sesmaria para as últimas 24h
            leituras_sesmaria = [
                (24 - i, Decimal(f"{1.60 + (i * 0.01):.2f}")) for i in range(25)
            ]
            await _seed_leituras(
                db,
                estacao=estacao_sesmaria,
                cotas={"atencao": Decimal("2.00"), "alerta": Decimal("2.50"), "emergencia": Decimal("3.20")},
                leituras_base=leituras_sesmaria,
            )

    print("Seed concluído com sucesso. Monitoramento configurado exclusivamente para o Rio Sesmaria.")


if __name__ == "__main__":
    asyncio.run(seed())

