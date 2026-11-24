"""Orquestra a coleta das fontes externas e persiste leituras e instantâneos da bacia."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import Any

import httpx
import structlog
from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import AsyncSessionLocal
from app.models.coleta import ColetaBacia
from app.models.estacao import EstacaoMonitoramento
from app.models.leitura import LeituraNivel, NivelRiscoEnum
from app.models.niveis_risco import NivelRisco
from app.schemas.estacao import CotasSchema
from app.services.classificacao_risco import classificar_risco
from app.services.coleta import fontes

logger = structlog.get_logger()

COTAS_PADRAO = (Decimal("2.00"), Decimal("2.50"), Decimal("3.20"))
RETENCAO_COLETAS_DIAS = 14
_trava = asyncio.Lock()


@dataclass
class ResultadoColeta:
    """Resumo de uma rodada de coleta."""

    coletado_em: datetime
    leituras_novas: int = 0
    fontes_ok: list[str] = field(default_factory=list)
    erros: dict[str, str] = field(default_factory=dict)


async def garantir_estacao(db: AsyncSession) -> tuple[EstacaoMonitoramento, NivelRisco]:
    """Garante a estação CEMADEN do Rio Sesmaria e suas cotas (idempotente)."""
    codigo = settings.CEMADEN_ESTACAO_CODIGO
    estacao = await db.scalar(
        select(EstacaoMonitoramento).where(EstacaoMonitoramento.codigo_externo == codigo)
    )
    if estacao is None:
        estacao = EstacaoMonitoramento(
            codigo_externo=codigo,
            nome="Estação CEMADEN Rio Sesmarias",
            rio="Rio Sesmaria",
            latitude=Decimal("-22.480500"),
            longitude=Decimal("-44.470100"),
            ativa=True,
        )
        db.add(estacao)
        await db.flush()
    cotas = await db.scalar(select(NivelRisco).where(NivelRisco.estacao_id == estacao.id))
    if cotas is None:
        cotas = NivelRisco(
            estacao_id=estacao.id,
            cota_atencao=COTAS_PADRAO[0],
            cota_alerta=COTAS_PADRAO[1],
            cota_emergencia=COTAS_PADRAO[2],
        )
        db.add(cotas)
        await db.flush()
    return estacao, cotas


def _serializar_funil(serie: list[tuple[Any, float]]) -> list[dict[str, Any]]:
    return [{"data": dia.isoformat(), "vazao_m3s": vazao} for dia, vazao in serie]


async def _coletar_fontes(
    resultado: ResultadoColeta,
) -> tuple[list[fontes.PontoNivel], dict[str, Any]]:
    """Consulta todas as fontes em paralelo; falhas isoladas não derrubam as demais."""
    timeout = httpx.Timeout(settings.HTTP_TIMEOUT_SEGUNDOS)
    estacao_id = settings.CEMADEN_ESTACAO_ID
    async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
        nomes = ["cemaden_nivel", "cemaden_chuva", "cemaden_imagem", "open_meteo", "ons_funil"]
        respostas = await asyncio.gather(
            fontes.buscar_nivel_cemaden(client, estacao_id),
            fontes.buscar_chuva_estacao(client, estacao_id),
            fontes.buscar_ultima_imagem(client, estacao_id),
            fontes.buscar_chuva_bacia(client),
            fontes.buscar_vazao_funil(client),
            return_exceptions=True,
        )
    dados: dict[str, Any] = {}
    for nome, resposta in zip(nomes, respostas, strict=True):
        if isinstance(resposta, BaseException):
            resultado.erros[nome] = str(resposta)
            logger.warning("coleta_fonte_falhou", fonte=nome, erro=str(resposta))
        else:
            dados[nome] = resposta
            resultado.fontes_ok.append(nome)

    payload: dict[str, Any] = {}
    if "open_meteo" in dados:
        payload["chuva"] = dados["open_meteo"]
    if "cemaden_chuva" in dados:
        chuva = dados["cemaden_chuva"]
        payload["chuva_estacao"] = {
            "ultima_hora_mm": chuva.ultima_hora_mm,
            "ultimas_24h_mm": chuva.ultimas_24h_mm,
            "data_hora": chuva.data_hora.isoformat() if chuva.data_hora else None,
        }
    imagem = dados.get("cemaden_imagem")
    if imagem is not None:
        payload["imagem"] = {"url": imagem.url, "data_hora": imagem.data_hora.isoformat()}
    if "ons_funil" in dados:
        payload["funil"] = _serializar_funil(dados["ons_funil"])
    return dados.get("cemaden_nivel", []), payload


async def executar_coleta() -> ResultadoColeta:
    """Executa uma rodada completa de coleta e grava no banco."""
    async with _trava:
        resultado = ResultadoColeta(coletado_em=datetime.now(UTC))
        pontos, payload = await _coletar_fontes(resultado)

        async with AsyncSessionLocal() as db:
            estacao, cotas = await garantir_estacao(db)
            schema_cotas = CotasSchema(
                atencao=cotas.cota_atencao,
                alerta=cotas.cota_alerta,
                emergencia=cotas.cota_emergencia,
            )
            if pontos:
                linhas = [
                    {
                        "estacao_id": estacao.id,
                        "data_hora": p.data_hora,
                        "nivel_metros": p.nivel,
                        "classificacao": NivelRiscoEnum(classificar_risco(p.nivel, schema_cotas)),
                        "fonte": f"CEMADEN {settings.CEMADEN_ESTACAO_CODIGO}",
                    }
                    for p in pontos
                ]
                resposta = await db.execute(
                    pg_insert(LeituraNivel)
                    .values(linhas)
                    .on_conflict_do_nothing(index_elements=["estacao_id", "data_hora"])
                    .returning(LeituraNivel.id)
                )
                resultado.leituras_novas = len(resposta.all())
            if payload:
                payload["coletado_em"] = resultado.coletado_em.isoformat()
                db.add(ColetaBacia(coletado_em=resultado.coletado_em, payload=payload))
            corte = resultado.coletado_em - timedelta(days=RETENCAO_COLETAS_DIAS)
            await db.execute(delete(ColetaBacia).where(ColetaBacia.coletado_em < corte))
            await db.commit()

        logger.info(
            "coleta_concluida",
            leituras_novas=resultado.leituras_novas,
            fontes_ok=resultado.fontes_ok,
            erros=list(resultado.erros),
        )
        return resultado
