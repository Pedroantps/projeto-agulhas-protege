"""Testes do modelo de previsão e das correlações calculadas sobre dados reais."""

from datetime import UTC, datetime, timedelta

from app.services.coleta import modelo

AGORA = datetime(2026, 11, 23, 12, 0, tzinfo=UTC)
COTAS = modelo.Cotas(2.0, 2.5, 3.2)


def _serie_chuva(por_hora: float, dias_passados: int = 7, dias_futuros: int = 4) -> dict:
    inicio = (AGORA + modelo.FUSO_LOCAL).replace(minute=0) - timedelta(days=dias_passados)
    total = 24 * (dias_passados + dias_futuros)
    horas = [(inicio + timedelta(hours=h)).strftime("%Y-%m-%dT%H:%M") for h in range(total)]
    return {"horas": horas, "precipitacao": [por_hora] * total, "probabilidade": [50.0] * total}


def _nivel(valor: float, horas: int = 96) -> modelo.Serie:
    return [(AGORA - timedelta(hours=horas - i), valor) for i in range(horas + 1)]


def test_sem_chuva_o_rio_recua_para_o_nivel_base() -> None:
    serie = _nivel(1.0)
    serie[-10:] = [(t, 1.5) for t, _ in serie[-10:]]
    chuva = {"resende": _serie_chuva(0), "cabeceira": _serie_chuva(0)}
    previsoes, _ = modelo.calcular_previsoes(serie, chuva, COTAS, 0.0, AGORA)
    niveis = [p.nivel_estimado for p in previsoes]
    assert niveis == sorted(niveis, reverse=True)
    assert niveis[0] < 1.5
    assert all(p.classificacao == "NORMAL" for p in previsoes)
    assert all(p.probabilidade_alerta == 0.0 for p in previsoes)


def test_chuva_forte_eleva_o_risco_e_as_probabilidades() -> None:
    chuva = {"resende": _serie_chuva(4.0), "cabeceira": _serie_chuva(6.0)}
    previsoes, condicoes = modelo.calcular_previsoes(_nivel(1.8), chuva, COTAS, 40.0, AGORA)
    assert previsoes[0].nivel_estimado > 1.8
    assert previsoes[0].chuva_prevista_mm > 100
    assert previsoes[0].probabilidade_alerta > 0
    assert condicoes["saturacao_solo_percent"] == 100.0


def test_classificar_segue_as_cotas() -> None:
    assert modelo.classificar(1.99, COTAS) == "NORMAL"
    assert modelo.classificar(2.0, COTAS) == "ATENCAO"
    assert modelo.classificar(2.5, COTAS) == "ALERTA"
    assert modelo.classificar(3.2, COTAS) == "EMERGENCIA"


def test_correlacao_defasada_detecta_relacao_com_atraso() -> None:
    chuva = _serie_chuva(0.0)
    # Pulsos de chuva a cada 7h; o nível responde 5h depois.
    for h in range(0, len(chuva["horas"]), 7):
        chuva["precipitacao"][h] = 10.0
    por_hora = modelo._chuva_por_hora_utc(chuva)  # noqa: SLF001
    instantes = [(AGORA - timedelta(hours=24 * 3 - h)).replace(minute=0) for h in range(24 * 3)]
    serie = [(t, 1.0 + 0.1 * por_hora.get(t - timedelta(hours=5), 0.0)) for t in instantes]
    assert modelo.correlacao_defasada(serie, chuva, 5) > 0.95
    assert modelo.correlacao_defasada(serie, chuva, 3) < 0.5


def test_pearson_casos_limite() -> None:
    assert modelo.pearson([1, 2, 3], [2, 4, 6]) == 1.0
    assert modelo.pearson([1, 1, 1], [1, 2, 3]) == 0.0
    assert modelo.pearson([], []) == 0.0


def test_relevancia_e_remanso() -> None:
    assert modelo.relevancia(-0.8) == "ALTA"
    assert modelo.relevancia(0.5) == "MEDIA"
    assert modelo.relevancia(0.1) == "MODERADA"
    assert modelo.situacao_remanso(200, "NORMAL") == "FAVORAVEL"
    assert modelo.situacao_remanso(350, "NORMAL") == "ALERTA_REMANSO"
    assert modelo.situacao_remanso(350, "ALERTA") == "REMANSO_CRITICO"
