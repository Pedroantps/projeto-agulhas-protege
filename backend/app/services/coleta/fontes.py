"""Clientes das fontes públicas de dados reais da bacia do Rio Sesmaria.

- CEMADEN: nível (radar na ponte), pluviômetro e câmera da estação 330420118H.
- Open-Meteo: chuva observada/prevista em Resende e na cabeceira (São José do Barreiro-SP).
- ONS (dados abertos): vazão defluente diária da Represa do Funil (Rio Paraíba do Sul).

As funções ``parse_*`` são puras e testáveis; as funções ``buscar_*`` fazem a requisição.
"""

from __future__ import annotations

import csv
import io
from dataclasses import dataclass
from datetime import UTC, date, datetime
from decimal import Decimal
from typing import Any

import httpx

CEMADEN_BASE = "https://resources.cemaden.gov.br/graficos/cemaden/hidro/resources/json"
CEMADEN_RESUMO_PLUVIOMETROS = "https://resources.cemaden.gov.br/graficos/interativo/getJson2.php"
CEMADEN_IMAGENS = "https://resources.cemaden.gov.br/imghidro/"
CEMADEN_MAX_HORAS = 96

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
ONS_URL = (
    "https://ons-aws-prod-opendata.s3.amazonaws.com/dataset/dados_hidrologicos_di/"
    "DADOS_HIDROLOGICOS_RES_{ano}.csv"
)

# O arquivo é lido só pelo final (Range), sem o cabeçalho; as colunas são fixas no ONS.
COLUNAS_ONS = [
    "id_subsistema", "nom_subsistema", "tip_reservatorio", "nom_bacia", "nom_ree",
    "id_reservatorio", "nom_reservatorio", "num_ordemcs", "cod_usina", "din_instante",
    "val_nivelmontante", "val_niveljusante", "val_volumeutilcon", "val_vazaoafluente",
    "val_vazaoturbinada", "val_vazaovertida", "val_vazaooutrasestruturas",
    "val_vazaodefluente",
]  # fmt: skip

PONTO_RESENDE = (-22.4805, -44.4701)
PONTO_CABECEIRA = (-22.6447, -44.5772)  # São José do Barreiro-SP


class FonteIndisponivelError(Exception):
    """Falha ao consultar uma fonte externa."""


@dataclass(frozen=True)
class PontoNivel:
    """Leitura horária do nível do rio."""

    data_hora: datetime
    nivel: Decimal


@dataclass(frozen=True)
class ChuvaEstacao:
    """Chuva medida pelo pluviômetro da estação."""

    ultima_hora_mm: float
    ultimas_24h_mm: float
    data_hora: datetime | None


@dataclass(frozen=True)
class ImagemEstacao:
    """Foto mais recente da câmera da estação."""

    url: str
    data_hora: datetime


# ── Parsers ───────────────────────────────────────────────────────────────


def _parse_gmt(valor: str) -> datetime:
    """'2026-11-13 00:00:00' (GMT) → datetime com fuso UTC."""
    return datetime.strptime(valor, "%Y-%m-%d %H:%M:%S").replace(tzinfo=UTC)


def parse_medidas_nivel(dados: list[dict[str, Any]]) -> list[PontoNivel]:
    """Converte a série do sensor radar (nível = offset - distância até a água)."""
    pontos: list[PontoNivel] = []
    for item in dados:
        valor = item.get("valor")
        if valor in (None, ""):
            continue
        offset = item.get("offset")
        nivel = (Decimal(str(offset)) if offset not in (None, "") else Decimal(0)) - Decimal(
            str(valor)
        )
        pontos.append(PontoNivel(_parse_gmt(item["datahora"]), nivel.quantize(Decimal("0.001"))))
    pontos.sort(key=lambda p: p.data_hora)
    return pontos


def parse_resumo_pluviometro(dados: list[dict[str, Any]], estacao_id: int) -> ChuvaEstacao:
    """Extrai a chuva da estação do resumo estadual do CEMADEN ("-" = sem dado)."""

    def numero(valor: object) -> float:
        return float(valor) if isinstance(valor, int | float) else 0.0

    estacao = next((d for d in dados if d.get("idestacao") == estacao_id), None)
    if estacao is None:
        return ChuvaEstacao(0.0, 0.0, None)
    data_hora: datetime | None = None
    try:
        data_hora = datetime.strptime(estacao["datahoraUltimovalor"], "%d/%m/%y %H:%M").replace(
            tzinfo=UTC
        )
    except (KeyError, ValueError):
        data_hora = None
    return ChuvaEstacao(numero(estacao.get("acc1hr")), numero(estacao.get("acc24hr")), data_hora)


def parse_imagem(dados: list[dict[str, Any]]) -> ImagemEstacao | None:
    """Pega a foto mais recente da câmera da estação."""
    if not dados:
        return None
    ultima = dados[0]
    caminho = str(ultima.get("path", ""))
    if "/sgrp/imghidro/" not in caminho:
        return None
    relativo = caminho.split("/sgrp/imghidro/", 1)[1]
    return ImagemEstacao(f"{CEMADEN_IMAGENS}{relativo}", _parse_gmt(ultima["datahora"]))


def parse_open_meteo(bruto: Any) -> dict[str, dict[str, list[Any]]]:
    """Normaliza a resposta (lista com um item por ponto) em séries por local."""
    itens = bruto if isinstance(bruto, list) else [bruto]
    if len(itens) < 2:
        msg = "Resposta do Open-Meteo incompleta."
        raise FonteIndisponivelError(msg)

    def serie(item: dict[str, Any]) -> dict[str, list[Any]]:
        horario = item["hourly"]
        return {
            "horas": list(horario["time"]),
            "precipitacao": [float(v or 0) for v in horario["precipitation"]],
            "probabilidade": [float(v or 0) for v in horario["precipitation_probability"]],
        }

    return {"resende": serie(itens[0]), "cabeceira": serie(itens[1])}


def parse_vazao_funil(texto_csv: str) -> list[tuple[date, float]]:
    """Filtra a vazão defluente diária (m³/s) da Represa do Funil (Paraíba do Sul)."""
    resultado: dict[date, float] = {}
    # A primeira linha é o cabeçalho (arquivo inteiro) ou um trecho cortado (Range): descartada.
    linhas = texto_csv.splitlines()[1:]
    leitor = csv.DictReader(io.StringIO("\n".join(linhas)), fieldnames=COLUNAS_ONS, delimiter=";")
    for linha in leitor:
        if (linha.get("id_reservatorio") or "").strip() != "PBFUNI":
            continue
        bruto = (linha.get("val_vazaodefluente") or "").strip()
        instante = (linha.get("din_instante") or "").strip()
        if not bruto or not instante:
            continue
        try:
            resultado[date.fromisoformat(instante)] = float(bruto)
        except ValueError:
            continue
    return sorted(resultado.items())


# ── Requisições ───────────────────────────────────────────────────────────


async def _get_json(client: httpx.AsyncClient, url: str, params: dict[str, Any]) -> Any:
    try:
        resposta = await client.get(url, params=params)
        resposta.raise_for_status()
        return resposta.json()
    except (httpx.HTTPError, ValueError) as erro:
        msg = f"Falha ao consultar {url}: {erro}"
        raise FonteIndisponivelError(msg) from erro


async def buscar_nivel_cemaden(
    client: httpx.AsyncClient, estacao_id: int, horas: int = CEMADEN_MAX_HORAS
) -> list[PontoNivel]:
    """Série horária do nível (no máximo ~4 dias)."""
    pag = min(max(horas, 1), CEMADEN_MAX_HORAS) + 1
    dados = await _get_json(
        client, f"{CEMADEN_BASE}/MedidaResource.php", {"est": estacao_id, "sen": 20, "pag": pag}
    )
    return parse_medidas_nivel(dados)


async def buscar_chuva_estacao(client: httpx.AsyncClient, estacao_id: int) -> ChuvaEstacao:
    """Chuva medida pelo pluviômetro da estação (atualizada a cada 10 min)."""
    dados = await _get_json(client, CEMADEN_RESUMO_PLUVIOMETROS, {"uf": "RJ"})
    return parse_resumo_pluviometro(dados, estacao_id)


async def buscar_ultima_imagem(client: httpx.AsyncClient, estacao_id: int) -> ImagemEstacao | None:
    """Foto mais recente da câmera da estação."""
    dados = await _get_json(
        client, f"{CEMADEN_BASE}/ImagemResource.php", {"est": estacao_id, "pag": 1}
    )
    return parse_imagem(dados)


async def buscar_chuva_bacia(client: httpx.AsyncClient) -> dict[str, dict[str, list[Any]]]:
    """Chuva dos últimos 7 dias e prevista para 4 dias, em Resende e na cabeceira."""
    parametros = {
        "latitude": f"{PONTO_RESENDE[0]},{PONTO_CABECEIRA[0]}",
        "longitude": f"{PONTO_RESENDE[1]},{PONTO_CABECEIRA[1]}",
        "hourly": "precipitation,precipitation_probability",
        "past_days": 7,
        "forecast_days": 4,
        "timezone": "America/Sao_Paulo",
    }
    return parse_open_meteo(await _get_json(client, OPEN_METEO_URL, parametros))


async def buscar_vazao_funil(client: httpx.AsyncClient) -> list[tuple[date, float]]:
    """Vazão defluente diária recente do Funil. Baixa só o final do arquivo anual (Range)."""
    ano = datetime.now(UTC).year
    try:
        resposta = await client.get(
            ONS_URL.format(ano=ano), headers={"Range": "bytes=-1500000"}, timeout=60.0
        )
        resposta.raise_for_status()
    except httpx.HTTPError as erro:
        msg = f"Falha ao consultar o ONS: {erro}"
        raise FonteIndisponivelError(msg) from erro
    serie = parse_vazao_funil(resposta.content.decode("utf-8", errors="replace"))
    if not serie:
        msg = "O ONS não retornou vazão do Funil."
        raise FonteIndisponivelError(msg)
    return serie[-15:]
