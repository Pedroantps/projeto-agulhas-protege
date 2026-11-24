"""Schemas para o subsistema de correlação hidrológica e IA do Rio Sesmaria."""

from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class CorrelacaoVariavel(BaseModel):
    """Item individual da análise de correlação estatística com a altura do rio."""

    model_config = ConfigDict(extra="forbid")

    id: str
    nome: str
    origem: str
    tipo: Literal["chuva_sjb_lag", "chuva_acumulada", "vazao_funil", "previsao"]
    lag_horas: str
    coeficiente_r: float = Field(..., ge=-1.0, le=1.0)
    relevancia: Literal["ALTA", "MEDIA", "MODERADA"]
    descricao_fisica: str


class PrevisaoNivelDia(BaseModel):
    """Previsão preditiva para horizontes de 1 a 3 dias (+24h, +48h, +72h)."""

    model_config = ConfigDict(extra="forbid")

    dia_offset: int = Field(..., ge=1, le=3)
    rotulo: str  # "+24h (Amanhã)", "+48h (2 dias)", "+72h (3 dias)"
    data_alvo: datetime
    chuva_prevista_mm: Decimal
    vazao_funil_esperada_m3s: Decimal
    nivel_estimado_metros: Decimal
    probabilidade_alerta: float = Field(..., ge=0.0, le=100.0)
    probabilidade_emergencia: float = Field(..., ge=0.0, le=100.0)
    classificacao_risco: Literal["NORMAL", "ATENCAO", "ALERTA", "EMERGENCIA"]
    confiabilidade_percentual: float = Field(..., ge=0.0, le=100.0)


class RecomendacaoFunil(BaseModel):
    """Recomendação operacional para a Represa do Funil (Efeito Remanso)."""

    model_config = ConfigDict(extra="forbid")

    vazao_atual_m3s: Decimal
    vazao_maxima_sugerida_m3s: Decimal
    tempo_transito_medio: str  # "1h20 a 1h30"
    situacao_remanso: Literal["FAVORAVEL", "ALERTA_REMANSO", "REMANSO_CRITICO"]
    acao_preventiva: str
    impacto_estimado_leito_cm: int  # redução estimada no nível do Sesmaria em cm


class TelemetriaBacia(BaseModel):
    """Instantâneo sincronizado dos pontos de medição da Bacia do Sesmaria."""

    model_config = ConfigDict(extra="forbid")

    # São José do Barreiro (Cabeceira)
    chuva_sjb_1h_lag4_mm: Decimal
    chuva_sjb_1h_lag5_mm: Decimal
    chuva_sjb_1h_lag6_mm: Decimal
    chuva_sjb_acumulada_12h_mm: Decimal
    chuva_sjb_acumulada_24h_mm: Decimal
    chuva_sjb_acumulada_48h_mm: Decimal
    chuva_sjb_acumulada_168h_mm: Decimal
    saturacao_solo_sjb_percent: float

    # Resende (Jusante)
    chuva_resende_acumulada_12h_mm: Decimal
    chuva_resende_acumulada_24h_mm: Decimal
    chuva_resende_acumulada_48h_mm: Decimal
    chuva_resende_acumulada_168h_mm: Decimal

    # Represa do Funil
    vazao_funil_atual_m3s: Decimal
    vazao_funil_lag1_m3s: Decimal
    vazao_funil_lag2_m3s: Decimal
    vazao_funil_media_transito_m3s: Decimal


class SesmariaDashboardResponse(BaseModel):
    """Payload consolidado do painel analítico e preditivo do Rio Sesmaria."""

    model_config = ConfigDict(extra="forbid")

    estacao_id: str
    nome: str
    rio: str
    municipio: str
    nivel_atual_metros: Decimal
    classificacao_risco: Literal["NORMAL", "ATENCAO", "ALERTA", "EMERGENCIA"]
    data_hora_leitura: datetime
    cota_atencao: Decimal
    cota_alerta: Decimal
    cota_emergencia: Decimal

    telemetria: TelemetriaBacia
    correlacoes: list[CorrelacaoVariavel]
    previsoes: list[PrevisaoNivelDia]
    recomendacao_funil: RecomendacaoFunil
    eventos_criticos_base: int  # Leituras reais da base em que o rio atingiu a cota de alerta
    mensagem_alerta_whatsapp: str

    # Procedência dos dados (tudo vem de coleta real executada pelo backend)
    dados_disponiveis: bool = True
    fonte_dados: str = ""
    coletado_em: datetime | None = None
    chuva_estacao_1h_mm: Decimal | None = None
    chuva_estacao_24h_mm: Decimal | None = None
    foto_estacao_url: str | None = None
    foto_estacao_data_hora: datetime | None = None
