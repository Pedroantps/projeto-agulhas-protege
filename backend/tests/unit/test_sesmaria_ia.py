"""Testes unitários do motor de correlação e cálculo preditivo do Rio Sesmaria."""

from decimal import Decimal

from app.schemas.sesmaria import PrevisaoNivelDia, RecomendacaoFunil
from app.services.sesmaria_ia_service import (
    calcular_correlacao_pearson,
    gerar_texto_whatsapp,
)


def test_calcular_correlacao_pearson_linear_perfeita():
    x = [1.0, 2.0, 3.0, 4.0, 5.0]
    y = [2.0, 4.0, 6.0, 8.0, 10.0]
    r = calcular_correlacao_pearson(x, y)
    assert r == 1.0


def test_calcular_correlacao_pearson_inversa():
    x = [1.0, 2.0, 3.0, 4.0, 5.0]
    y = [10.0, 8.0, 6.0, 4.0, 2.0]
    r = calcular_correlacao_pearson(x, y)
    assert r == -1.0


def test_calcular_correlacao_pearson_tamanhos_insuficientes():
    assert calcular_correlacao_pearson([], []) == 0.0
    assert calcular_correlacao_pearson([1.0], [2.0]) == 0.0
    assert calcular_correlacao_pearson([1.0, 2.0], [3.0]) == 0.0


def test_calcular_correlacao_pearson_variancia_zero():
    x = [2.0, 2.0, 2.0]
    y = [1.0, 2.0, 3.0]
    assert calcular_correlacao_pearson(x, y) == 0.0


def test_gerar_texto_whatsapp_estrutura():
    previsao = PrevisaoNivelDia(
        dia_offset=1,
        rotulo="+24h",
        data_alvo="2026-09-22T00:00:00Z",
        chuva_prevista_mm=Decimal("35.0"),
        vazao_funil_esperada_m3s=Decimal("400.0"),
        nivel_estimado_metros=Decimal("2.65"),
        probabilidade_alerta=80.0,
        probabilidade_emergencia=20.0,
        classificacao_risco="ALERTA",
        confiabilidade_percentual=85.0,
    )
    rec = RecomendacaoFunil(
        vazao_atual_m3s=Decimal("380.0"),
        vazao_maxima_sugerida_m3s=Decimal("310.0"),
        tempo_transito_medio="1h20 a 1h30",
        situacao_remanso="ALERTA_REMANSO",
        acao_preventiva="Reduzir vazão do Funil",
        impacto_estimado_leito_cm=20,
    )

    texto = gerar_texto_whatsapp(
        nome_estacao="Estação Parque Ipiranga",
        nivel_atual=Decimal("1.85"),
        classificacao="NORMAL",
        chuva_sjb_lag5=Decimal("15.2"),
        vazao_funil=Decimal("380.0"),
        previsao_24h=previsao,
        recomendacao=rec,
    )

    assert "ALERTA DEFESA CIVIL" in texto
    assert "Parque Ipiranga" in texto
    assert "1.85m (NORMAL)" in texto
    assert "São José do Barreiro -5h" in texto
    assert "Previsão +24h" in texto
    assert "Reduzir vazão do Funil" in texto
