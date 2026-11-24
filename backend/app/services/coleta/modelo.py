"""Modelo hidrológico simplificado e estatísticas calculadas sobre dados reais coletados.

Não é uma rede neural: é um modelo de tanque linear com cenários de chuva, calibrável e
auditável. Os coeficientes são aproximações e não substituem a modelagem oficial.

- A chuva da cabeceira (São José do Barreiro) pesa 60% e a de Resende 40%.
- O escoamento cresce com a chuva antecedente (saturação do solo).
- Sem chuva o rio recua 20% por dia em direção ao nível de base (mínimo recente).
- A probabilidade de ALERTA/EMERGÊNCIA é a fração de cenários de chuva (×0,5 a ×2) que
  ultrapassa a cota.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from typing import Any

PESO_CABECEIRA = 0.6
PESO_RESENDE = 0.4
METROS_POR_MM = 0.025
RECESSAO_DIARIA = 0.8
CENARIOS_CHUVA = (0.5, 0.75, 1.0, 1.25, 1.5, 2.0)
CONFIABILIDADE_POR_DIA = (85.0, 70.0, 55.0)
ROTULOS = ("+24h (Amanhã)", "+48h (2 dias)", "+72h (3 dias)")
FUSO_LOCAL = timedelta(hours=-3)  # America/Sao_Paulo (sem horário de verão)

Serie = list[tuple[datetime, float]]


@dataclass(frozen=True)
class Cotas:
    """Cotas de risco em metros."""

    atencao: float
    alerta: float
    emergencia: float

    @classmethod
    def de_decimais(cls, atencao: Decimal, alerta: Decimal, emergencia: Decimal) -> Cotas:
        return cls(float(atencao), float(alerta), float(emergencia))


def classificar(nivel: float, cotas: Cotas) -> str:
    """Mesma regra de ``classificar_risco`` do backend."""
    if nivel >= cotas.emergencia:
        return "EMERGENCIA"
    if nivel >= cotas.alerta:
        return "ALERTA"
    if nivel >= cotas.atencao:
        return "ATENCAO"
    return "NORMAL"


@dataclass(frozen=True)
class PrevisaoCalculada:
    """Previsão de um dia à frente."""

    dia_offset: int
    rotulo: str
    data_alvo: datetime
    chuva_prevista_mm: float
    nivel_estimado: float
    probabilidade_alerta: float
    probabilidade_emergencia: float
    classificacao: str
    confiabilidade: float


# ── Chuva ─────────────────────────────────────────────────────────────────


def hora_local_para_utc(texto: str) -> datetime:
    """'2026-11-13T14:00' (horário de Brasília) → datetime UTC."""
    return datetime.fromisoformat(texto).replace(tzinfo=UTC) - FUSO_LOCAL


def indice_agora(horas: list[str], agora: datetime | None = None) -> int:
    """Índice da hora atual na série do Open-Meteo (horário local)."""
    referencia = (agora or datetime.now(UTC)) + FUSO_LOCAL
    alvo = referencia.strftime("%Y-%m-%dT%H")
    for i, hora in enumerate(horas):
        if hora[:13] == alvo:
            return i
    return min(len(horas) - 1, 24 * 7)


def somar(valores: list[float], inicio: int, fim: int) -> float:
    """Soma segura de uma janela da série."""
    return float(sum(valores[max(0, inicio) : max(0, fim)]))


# ── Estatística ───────────────────────────────────────────────────────────


def pearson(x: list[float], y: list[float]) -> float:
    """Coeficiente r de Pearson (idêntico ao CORREL do Excel)."""
    if len(x) != len(y) or len(x) < 2:
        return 0.0
    n = len(x)
    media_x = sum(x) / n
    media_y = sum(y) / n
    numerador = sum((a - media_x) * (b - media_y) for a, b in zip(x, y, strict=True))
    den_x = sum((a - media_x) ** 2 for a in x)
    den_y = sum((b - media_y) ** 2 for b in y)
    denominador = (den_x * den_y) ** 0.5
    if denominador == 0:
        return 0.0
    return round(numerador / denominador, 3)


def relevancia(r: float) -> str:
    """Classifica a força da correlação."""
    forca = abs(r)
    if forca >= 0.7:
        return "ALTA"
    if forca >= 0.4:
        return "MEDIA"
    return "MODERADA"


def _chuva_por_hora_utc(chuva: dict[str, list[Any]]) -> dict[datetime, float]:
    return {
        hora_local_para_utc(h): float(p)
        for h, p in zip(chuva["horas"], chuva["precipitacao"], strict=True)
    }


def correlacao_defasada(serie_nivel: Serie, chuva: dict[str, list[Any]], lag_horas: int) -> float:
    """r entre a chuva ``lag_horas`` antes e o nível em cada hora."""
    por_hora = _chuva_por_hora_utc(chuva)
    xs: list[float] = []
    ys: list[float] = []
    for instante, nivel in serie_nivel:
        base = instante.replace(minute=0, second=0, microsecond=0) - timedelta(hours=lag_horas)
        if base in por_hora:
            xs.append(por_hora[base])
            ys.append(nivel)
    return pearson(xs, ys)


def correlacao_acumulada(serie_nivel: Serie, chuva: dict[str, list[Any]], janela_h: int) -> float:
    """r entre a chuva acumulada nas ``janela_h`` horas anteriores e o nível."""
    por_hora = _chuva_por_hora_utc(chuva)
    xs: list[float] = []
    ys: list[float] = []
    for instante, nivel in serie_nivel:
        fim = instante.replace(minute=0, second=0, microsecond=0)
        horas = [fim - timedelta(hours=k) for k in range(janela_h)]
        if all(h in por_hora for h in horas):
            xs.append(sum(por_hora[h] for h in horas))
            ys.append(nivel)
    return pearson(xs, ys)


def correlacao_funil(serie_nivel: Serie, funil: list[tuple[date, float]]) -> float:
    """r entre a vazão defluente do Funil (dia anterior) e o nível médio diário."""
    medias: dict[date, list[float]] = {}
    for instante, nivel in serie_nivel:
        medias.setdefault(instante.date(), []).append(nivel)
    vazoes = dict(funil)
    xs: list[float] = []
    ys: list[float] = []
    for dia, niveis in medias.items():
        anterior = dia - timedelta(days=1)
        if anterior in vazoes:
            xs.append(vazoes[anterior])
            ys.append(sum(niveis) / len(niveis))
    return pearson(xs, ys) if len(xs) >= 4 else 0.0


# ── Previsão ──────────────────────────────────────────────────────────────


def _simular(
    nivel_atual: float,
    nivel_base: float,
    antecedente_inicial: float,
    onda_em_curso: float,
    chuvas_dia: list[tuple[float, float]],
    multiplicador: float,
) -> list[float]:
    nivel = nivel_atual
    antecedente = antecedente_inicial
    niveis: list[float] = []
    for i, (chuva_resende, chuva_cabeceira) in enumerate(chuvas_dia):
        efetiva = (PESO_CABECEIRA * chuva_cabeceira + PESO_RESENDE * chuva_resende) * multiplicador
        coeficiente = min(0.6, 0.2 + antecedente / 150)
        nivel = (
            nivel_base
            + (nivel - nivel_base) * RECESSAO_DIARIA
            + coeficiente * efetiva * METROS_POR_MM
            + (onda_em_curso if i == 0 else 0.0)
        )
        antecedente = antecedente / 2 + efetiva
        niveis.append(nivel)
    return niveis


def calcular_previsoes(
    serie_nivel: Serie,
    chuva: dict[str, dict[str, list[Any]]],
    cotas: Cotas,
    chuva_medida_24h_estacao: float = 0.0,
    agora: datetime | None = None,
) -> tuple[list[PrevisaoCalculada], dict[str, float | None]]:
    """Calcula +24h/+48h/+72h e devolve também as condições atuais da bacia."""
    momento = agora or datetime.now(UTC)
    ultimos = serie_nivel[-97:]
    nivel_atual = ultimos[-1][1]
    nivel_base = min(n for _, n in ultimos)
    resende = chuva["resende"]
    cabeceira = chuva["cabeceira"]
    idx = indice_agora(resende["horas"], momento)

    chuva_48_resende = max(chuva_medida_24h_estacao, somar(resende["precipitacao"], idx - 48, idx))
    antecedente = (
        PESO_CABECEIRA * somar(cabeceira["precipitacao"], idx - 48, idx)
        + PESO_RESENDE * chuva_48_resende
    )

    alvo = ultimos[-1][0] - timedelta(hours=6)
    seis_horas = next((n for t, n in ultimos if t >= alvo), None)
    tendencia = nivel_atual - seis_horas if seis_horas is not None else None
    onda = max(0.0, tendencia or 0.0) * 0.5

    chuvas_dia: list[tuple[float, float]] = []
    probabilidade_chuva: list[float] = []
    for i in range(3):
        ini, fim = idx + i * 24, idx + (i + 1) * 24
        chuvas_dia.append(
            (somar(resende["precipitacao"], ini, fim), somar(cabeceira["precipitacao"], ini, fim))
        )
        janela = resende["probabilidade"][ini:fim]
        probabilidade_chuva.append(max(janela) if janela else 0.0)

    base = _simular(nivel_atual, nivel_base, antecedente, onda, chuvas_dia, 1.0)
    cenarios = [
        _simular(nivel_atual, nivel_base, antecedente, onda, chuvas_dia, m) for m in CENARIOS_CHUVA
    ]
    previsoes: list[PrevisaoCalculada] = []
    for i, nivel in enumerate(base):
        n_alerta = sum(1 for c in cenarios if c[i] >= cotas.alerta)
        n_emergencia = sum(1 for c in cenarios if c[i] >= cotas.emergencia)
        previsoes.append(
            PrevisaoCalculada(
                dia_offset=i + 1,
                rotulo=ROTULOS[i],
                data_alvo=momento + timedelta(days=i + 1),
                chuva_prevista_mm=round(
                    PESO_CABECEIRA * chuvas_dia[i][1] + PESO_RESENDE * chuvas_dia[i][0], 1
                ),
                nivel_estimado=round(nivel, 2),
                probabilidade_alerta=round(100 * n_alerta / len(cenarios), 1),
                probabilidade_emergencia=round(100 * n_emergencia / len(cenarios), 1),
                classificacao=classificar(nivel, cotas),
                confiabilidade=CONFIABILIDADE_POR_DIA[i],
            )
        )
    condicoes: dict[str, float | None] = {
        "saturacao_solo_percent": round(min(100.0, antecedente / 80 * 100), 1),
        "tendencia_6h": tendencia,
    }
    return previsoes, condicoes


# ── Funil ─────────────────────────────────────────────────────────────────


def situacao_remanso(vazao_m3s: float, pior_risco_previsto: str) -> str:
    """Heurística do efeito remanso: vazão alta no Paraíba do Sul dificulta a drenagem do Sesmaria."""
    risco_previsto = pior_risco_previsto in ("ALERTA", "EMERGENCIA")
    if vazao_m3s >= 300 and risco_previsto:
        return "REMANSO_CRITICO"
    if vazao_m3s >= 300 or risco_previsto:
        return "ALERTA_REMANSO"
    return "FAVORAVEL"
