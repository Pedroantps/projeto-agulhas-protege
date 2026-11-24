"""Testes dos parsers das fontes externas (CEMADEN, Open-Meteo, ONS)."""

from datetime import UTC, date, datetime
from decimal import Decimal

import pytest

from app.services.coleta import fontes


def test_parse_medidas_nivel_calcula_offset_menos_valor() -> None:
    dados = [
        {"datahora": "2026-11-23 20:00:00", "valor": "11.027", "offset": "12.1645"},
        {"datahora": "2026-11-23 19:00:00", "valor": "11.008", "offset": "12.1645"},
        {"datahora": "2026-11-23 21:00:00", "valor": None, "offset": "12.1645"},
    ]
    pontos = fontes.parse_medidas_nivel(dados)
    assert [p.nivel for p in pontos] == [Decimal("1.156"), Decimal("1.138")]
    assert pontos[0].data_hora == datetime(2026, 11, 23, 19, tzinfo=UTC)
    assert len(pontos) == 2


def test_parse_resumo_pluviometro_ignora_traco() -> None:
    dados = [
        {"idestacao": 1, "acc1hr": 5, "acc24hr": 9, "datahoraUltimovalor": "23/11/26 23:00"},
        {
            "idestacao": 8799,
            "acc1hr": "-",
            "acc24hr": 12.4,
            "datahoraUltimovalor": "23/11/26 23:00",
        },
    ]
    chuva = fontes.parse_resumo_pluviometro(dados, 8799)
    assert chuva.ultima_hora_mm == 0.0
    assert chuva.ultimas_24h_mm == 12.4
    assert chuva.data_hora == datetime(2026, 11, 23, 23, 0, tzinfo=UTC)


def test_parse_resumo_pluviometro_estacao_ausente() -> None:
    assert fontes.parse_resumo_pluviometro([], 8799).ultimas_24h_mm == 0.0


def test_parse_imagem_monta_url_publica() -> None:
    dados = [
        {
            "datahora": "2026-11-23 23:00:03",
            "path": "/dados/sgrp/imghidro/RJ/330420118H/Nivel-330420118H-20261123230003.jpg",
        }
    ]
    imagem = fontes.parse_imagem(dados)
    assert imagem is not None
    assert imagem.url == (
        "https://resources.cemaden.gov.br/imghidro/RJ/330420118H/Nivel-330420118H-20261123230003.jpg"
    )
    assert fontes.parse_imagem([]) is None


def test_parse_open_meteo_separa_locais() -> None:
    item = {
        "hourly": {
            "time": ["2026-11-23T00:00", "2026-11-23T01:00"],
            "precipitation": [0.2, None],
            "precipitation_probability": [10, None],
        }
    }
    series = fontes.parse_open_meteo([item, item])
    assert series["resende"]["precipitacao"] == [0.2, 0.0]
    assert series["cabeceira"]["probabilidade"] == [10.0, 0.0]


def test_parse_open_meteo_incompleto_levanta_erro() -> None:
    with pytest.raises(fontes.FonteIndisponivelError):
        fontes.parse_open_meteo({"hourly": {}})


def test_parse_vazao_funil_filtra_reservatorio() -> None:

    def linha(reservatorio: str, dia: str, defluente: str) -> str:
        campos = [""] * len(fontes.COLUNAS_ONS)
        campos[fontes.COLUNAS_ONS.index("id_reservatorio")] = reservatorio
        campos[fontes.COLUNAS_ONS.index("din_instante")] = dia
        campos[fontes.COLUNAS_ONS.index("val_vazaodefluente")] = defluente
        return ";".join(campos)

    csv_texto = "\n".join(
        [
            "trecho cortado de um Range;;;",
            linha("PBFUNI", "2026-11-21", "204.0"),
            linha("GRFUNI", "2026-11-21", "355.0"),
            linha("PBFUNI", "2026-11-22", "197.0"),
            linha("PBFUNI", "2026-11-23", ""),
        ]
    )
    assert fontes.parse_vazao_funil(csv_texto) == [
        (date(2026, 11, 21), 204.0),
        (date(2026, 11, 22), 197.0),
    ]
