"""Serviço do painel analítico do Rio Sesmaria, calculado sobre dados reais coletados."""

from __future__ import annotations

from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.coleta import ColetaBacia
from app.models.estacao import EstacaoMonitoramento
from app.models.leitura import LeituraNivel
from app.models.niveis_risco import NivelRisco
from app.schemas.sesmaria import (
    CorrelacaoVariavel,
    PrevisaoNivelDia,
    RecomendacaoFunil,
    SesmariaDashboardResponse,
    TelemetriaBacia,
)
from app.services.coleta import modelo

JANELA_BASE_HORAS = 24 * 90
JANELA_CORRELACAO_HORAS = 24 * 14
ORDEM_RISCO = ["NORMAL", "ATENCAO", "ALERTA", "EMERGENCIA"]
REDUCAO_SUGERIDA_FUNIL = 0.15
CM_POR_M3S_REDUZIDO = 0.4  # relação herdada do estudo original; heurística sujeita a calibração


def calcular_correlacao_pearson(x: list[float], y: list[float]) -> float:
    """Coeficiente r de Pearson entre duas séries (idêntico ao CORREL do Excel)."""
    return modelo.pearson(x, y)


def gerar_texto_whatsapp(
    nome_estacao: str,
    nivel_atual: Decimal,
    classificacao: str,
    chuva_sjb_lag5: Decimal,
    vazao_funil: Decimal,
    previsao_24h: PrevisaoNivelDia,
    recomendacao: RecomendacaoFunil,
) -> str:
    """Gera mensagem formatada para acionamento rápido da Defesa Civil."""
    return (
        f"🚨 *ALERTA DEFESA CIVIL — MONITORAMENTO RIO SESMARIA*\n"
        f"📍 *Estação:* {nome_estacao} (Resende-RJ)\n"
        f"🌊 *Nível Atual:* {nivel_atual:.2f}m ({classificacao})\n"
        f"🌧️ *Chuva Montante (São José do Barreiro -5h):* {chuva_sjb_lag5:.1f} mm/h\n"
        f"⏱️ *Vazão Represa do Funil:* {vazao_funil:.0f} m³/s (Trânsito: {recomendacao.tempo_transito_medio})\n"
        f"🔮 *Previsão +24h:* {previsao_24h.nivel_estimado_metros:.2f}m ({previsao_24h.classificacao_risco}) "
        f"| Chuva Prevista: {previsao_24h.chuva_prevista_mm:.1f}mm\n"
        f"⚠️ *Ação Recomendada no Funil:* {recomendacao.acao_preventiva}\n"
        f"🌐 *Painel Completo:* {settings.PUBLIC_URL}"
    )


def _chuva_zerada(agora: datetime) -> dict[str, dict[str, list[Any]]]:
    """Séries de chuva zeradas (7 dias passados + 4 futuros) quando não há coleta."""
    inicio = (agora + modelo.FUSO_LOCAL).replace(minute=0, second=0, microsecond=0)
    inicio -= timedelta(days=7)
    horas = [(inicio + timedelta(hours=h)).strftime("%Y-%m-%dT%H:%M") for h in range(24 * 11)]
    serie = {
        "horas": horas,
        "precipitacao": [0.0] * len(horas),
        "probabilidade": [0.0] * len(horas),
    }
    return {"resende": dict(serie), "cabeceira": dict(serie)}


async def _estacao_e_cotas(db: AsyncSession) -> tuple[EstacaoMonitoramento, NivelRisco]:
    resultado = await db.execute(
        select(EstacaoMonitoramento, NivelRisco)
        .join(NivelRisco, NivelRisco.estacao_id == EstacaoMonitoramento.id)
        .where(EstacaoMonitoramento.codigo_externo == settings.CEMADEN_ESTACAO_CODIGO)
        .where(EstacaoMonitoramento.ativa == True)  # noqa: E712
    )
    linha = resultado.first()
    if linha is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Estação do Rio Sesmaria ainda não cadastrada. Aguarde a primeira coleta.",
        )
    return linha[0], linha[1]


def _parse_dt(valor: str | None) -> datetime | None:
    return datetime.fromisoformat(valor) if valor else None


def _dec(valor: float, casas: int = 1) -> Decimal:
    return Decimal(str(round(valor, casas)))


def _montar_correlacoes(
    serie: modelo.Serie,
    chuva: dict[str, dict[str, list[Any]]] | None,
    funil: list[tuple[date, float]],
) -> list[CorrelacaoVariavel]:
    def item(
        id_: str, nome: str, origem: str, tipo: str, lag: str, r: float, descricao: str
    ) -> CorrelacaoVariavel:
        return CorrelacaoVariavel(
            id=id_,
            nome=nome,
            origem=origem,
            tipo=tipo,  # type: ignore[arg-type]
            lag_horas=lag,
            coeficiente_r=r,
            relevancia=modelo.relevancia(r),  # type: ignore[arg-type]
            descricao_fisica=descricao,
        )

    cab = chuva["cabeceira"] if chuva else None
    res = chuva["resende"] if chuva else None

    def r_lag(lag: int) -> float:
        return modelo.correlacao_defasada(serie, cab, lag) if cab else 0.0

    def r_acum(janela: int) -> float:
        if not cab or not res:
            return 0.0
        combinada = {
            "horas": cab["horas"],
            "precipitacao": [
                modelo.PESO_CABECEIRA * a + modelo.PESO_RESENDE * b
                for a, b in zip(cab["precipitacao"], res["precipitacao"], strict=False)
            ],
        }
        return modelo.correlacao_acumulada(serie, combinada, janela)

    origem_chuva = "Open-Meteo (reanálise horária)"
    return [
        item(
            "corr-sjb-lag5",
            "Chuva Horária São José do Barreiro (-5h)",
            origem_chuva,
            "chuva_sjb_lag",
            "-5 horas",
            r_lag(5),
            "Onda de cheia descendo a Serra da Bocaina até a área urbana de Resende.",
        ),
        item(
            "corr-sjb-lag4",
            "Chuva Horária São José do Barreiro (-4h)",
            origem_chuva,
            "chuva_sjb_lag",
            "-4 horas",
            r_lag(4),
            "Início da frente de onda escoando pelo leito superior.",
        ),
        item(
            "corr-sjb-lag6",
            "Chuva Horária São José do Barreiro (-6h)",
            origem_chuva,
            "chuva_sjb_lag",
            "-6 horas",
            r_lag(6),
            "Recarga residual das microbacias mais distantes da cabeceira.",
        ),
        item(
            "corr-saturacao-48h",
            "Chuva Acumulada 48h (SJB + Resende)",
            origem_chuva,
            "chuva_acumulada",
            "Janela 48h",
            r_acum(48),
            "Índice de saturação do solo: solo saturado converte mais chuva em escoamento.",
        ),
        item(
            "corr-saturacao-168h",
            "Chuva Acumulada 7 Dias (168h)",
            origem_chuva,
            "chuva_acumulada",
            "Janela 7 dias",
            r_acum(168),
            "Resposta basal da bacia (lençol freático e recarga).",
        ),
        item(
            "corr-funil-transito",
            "Vazão defluente da Represa do Funil (dia anterior)",
            "ONS — Dados Abertos",
            "vazao_funil",
            "1 dia",
            modelo.correlacao_funil(serie, funil),
            "Efeito remanso: vazão elevada no Paraíba do Sul dificulta a drenagem na foz do Sesmaria.",
        ),
    ]


async def obter_dashboard_sesmaria(db: AsyncSession) -> SesmariaDashboardResponse:
    """Calcula o painel analítico a partir das leituras e coletas reais gravadas no banco."""
    agora = datetime.now(UTC)
    estacao, cotas_db = await _estacao_e_cotas(db)

    leituras_res = await db.execute(
        select(LeituraNivel)
        .where(
            LeituraNivel.estacao_id == estacao.id,
            LeituraNivel.data_hora >= agora - timedelta(hours=JANELA_BASE_HORAS),
        )
        .order_by(LeituraNivel.data_hora.asc())
    )
    leituras = list(leituras_res.scalars().all())
    if not leituras:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Ainda não há leituras reais. Aguarde a primeira coleta do CEMADEN.",
        )

    coleta_res = await db.execute(
        select(ColetaBacia).order_by(ColetaBacia.coletado_em.desc()).limit(1)
    )
    coleta = coleta_res.scalars().first()
    payload: dict[str, Any] = coleta.payload if coleta else {}

    cotas = modelo.Cotas.de_decimais(
        cotas_db.cota_atencao, cotas_db.cota_alerta, cotas_db.cota_emergencia
    )
    serie_total: modelo.Serie = [(lei.data_hora, float(lei.nivel_metros)) for lei in leituras]
    serie_recente = [
        p for p in serie_total if p[0] >= agora - timedelta(hours=JANELA_CORRELACAO_HORAS)
    ]
    ultima = leituras[-1]
    nivel_atual = ultima.nivel_metros
    classificacao = modelo.classificar(float(nivel_atual), cotas)

    chuva = payload.get("chuva")
    chuva_estacao = payload.get("chuva_estacao") or {}
    funil = [
        (date.fromisoformat(f["data"]), float(f["vazao_m3s"])) for f in payload.get("funil", [])
    ]
    medida_24h = float(chuva_estacao.get("ultimas_24h_mm", 0.0))

    series_chuva = chuva or _chuva_zerada(agora)
    calculadas, condicoes = modelo.calcular_previsoes(
        serie_total, series_chuva, cotas, medida_24h, agora
    )

    # Telemetria da bacia
    cab, res = series_chuva["cabeceira"], series_chuva["resende"]
    idx = modelo.indice_agora(res["horas"], agora)

    def horas_atras(serie: dict[str, list[Any]], h: int) -> float:
        pos = idx - h
        return float(serie["precipitacao"][pos]) if 0 <= pos < len(serie["precipitacao"]) else 0.0

    def acum(serie: dict[str, list[Any]], h: int) -> float:
        return modelo.somar(serie["precipitacao"], idx - h, idx)

    vazoes = [v for _, v in funil]
    vazao_atual = vazoes[-1] if vazoes else 0.0
    telemetria = TelemetriaBacia(
        chuva_sjb_1h_lag4_mm=_dec(horas_atras(cab, 4)),
        chuva_sjb_1h_lag5_mm=_dec(horas_atras(cab, 5)),
        chuva_sjb_1h_lag6_mm=_dec(horas_atras(cab, 6)),
        chuva_sjb_acumulada_12h_mm=_dec(acum(cab, 12)),
        chuva_sjb_acumulada_24h_mm=_dec(acum(cab, 24)),
        chuva_sjb_acumulada_48h_mm=_dec(acum(cab, 48)),
        chuva_sjb_acumulada_168h_mm=_dec(acum(cab, 168)),
        saturacao_solo_sjb_percent=float(condicoes["saturacao_solo_percent"] or 0.0),
        chuva_resende_acumulada_12h_mm=_dec(acum(res, 12)),
        chuva_resende_acumulada_24h_mm=_dec(max(medida_24h, acum(res, 24))),
        chuva_resende_acumulada_48h_mm=_dec(max(medida_24h, acum(res, 48))),
        chuva_resende_acumulada_168h_mm=_dec(acum(res, 168)),
        vazao_funil_atual_m3s=_dec(vazao_atual),
        vazao_funil_lag1_m3s=_dec(vazoes[-2] if len(vazoes) >= 2 else 0.0),
        vazao_funil_lag2_m3s=_dec(vazoes[-3] if len(vazoes) >= 3 else 0.0),
        vazao_funil_media_transito_m3s=_dec(sum(vazoes[-3:]) / len(vazoes[-3:]) if vazoes else 0.0),
    )

    previsoes = [
        PrevisaoNivelDia(
            dia_offset=p.dia_offset,
            rotulo=p.rotulo,
            data_alvo=p.data_alvo,
            chuva_prevista_mm=_dec(p.chuva_prevista_mm),
            vazao_funil_esperada_m3s=_dec(vazao_atual),
            nivel_estimado_metros=_dec(p.nivel_estimado, 2),
            probabilidade_alerta=p.probabilidade_alerta,
            probabilidade_emergencia=p.probabilidade_emergencia,
            classificacao_risco=p.classificacao,  # type: ignore[arg-type]
            confiabilidade_percentual=p.confiabilidade,
        )
        for p in calculadas
    ]

    pior = max((p.classificacao_risco for p in previsoes), key=ORDEM_RISCO.index)
    if not vazoes:
        recomendacao = RecomendacaoFunil(
            vazao_atual_m3s=Decimal(0),
            vazao_maxima_sugerida_m3s=Decimal(0),
            tempo_transito_medio="1h20 a 1h30",
            situacao_remanso="FAVORAVEL",
            acao_preventiva="Vazão do Funil indisponível no momento (fonte ONS). Acompanhe o ONS.",
            impacto_estimado_leito_cm=0,
        )
    else:
        situacao = modelo.situacao_remanso(vazao_atual, pior)
        if situacao == "FAVORAVEL":
            sugerida, impacto = vazao_atual, 0
            acao = "Manter a operação atual do Funil: sem risco previsto de remanso no Sesmaria."
        else:
            sugerida = round(vazao_atual * (1 - REDUCAO_SUGERIDA_FUNIL))
            impacto = round((vazao_atual - sugerida) * CM_POR_M3S_REDUZIDO)
            acao = (
                f"Avaliar redução da vazão defluente de {vazao_atual:.0f} m³/s para "
                f"{sugerida:.0f} m³/s com ~1h30 de antecedência ao pico de chuva previsto "
                f"(risco previsto: {pior}). Estimativa heurística de ~{impacto} cm a menos "
                "no remanso da foz do Sesmaria."
            )
        recomendacao = RecomendacaoFunil(
            vazao_atual_m3s=_dec(vazao_atual),
            vazao_maxima_sugerida_m3s=_dec(sugerida),
            tempo_transito_medio="1h20 a 1h30",
            situacao_remanso=situacao,  # type: ignore[arg-type]
            acao_preventiva=acao,
            impacto_estimado_leito_cm=impacto,
        )

    texto_whatsapp = gerar_texto_whatsapp(
        nome_estacao=estacao.nome,
        nivel_atual=nivel_atual,
        classificacao=classificacao,
        chuva_sjb_lag5=telemetria.chuva_sjb_1h_lag5_mm,
        vazao_funil=telemetria.vazao_funil_atual_m3s,
        previsao_24h=previsoes[0],
        recomendacao=recomendacao,
    )

    fontes_ativas = [f"CEMADEN {settings.CEMADEN_ESTACAO_CODIGO}"]
    if chuva:
        fontes_ativas.append("Open-Meteo")
    if funil:
        fontes_ativas.append("ONS (Funil)")
    imagem = payload.get("imagem") or {}

    return SesmariaDashboardResponse(
        estacao_id=str(estacao.id),
        nome=estacao.nome,
        rio=estacao.rio,
        municipio="Resende-RJ",
        nivel_atual_metros=nivel_atual,
        classificacao_risco=classificacao,  # type: ignore[arg-type]
        data_hora_leitura=ultima.data_hora,
        cota_atencao=cotas_db.cota_atencao,
        cota_alerta=cotas_db.cota_alerta,
        cota_emergencia=cotas_db.cota_emergencia,
        telemetria=telemetria,
        correlacoes=_montar_correlacoes(serie_recente, chuva, funil),
        previsoes=previsoes,
        recomendacao_funil=recomendacao,
        eventos_criticos_base=sum(1 for _, n in serie_total if n >= cotas.alerta),
        mensagem_alerta_whatsapp=texto_whatsapp,
        dados_disponiveis=bool(chuva),
        fonte_dados=" · ".join(fontes_ativas),
        coletado_em=coleta.coletado_em if coleta else None,
        chuva_estacao_1h_mm=_dec(float(chuva_estacao["ultima_hora_mm"])) if chuva_estacao else None,
        chuva_estacao_24h_mm=_dec(medida_24h) if chuva_estacao else None,
        foto_estacao_url=imagem.get("url"),
        foto_estacao_data_hora=_parse_dt(imagem.get("data_hora")),
    )
