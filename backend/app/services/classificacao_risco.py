"""Motor de classificação de risco hidrológico e consulta de status das estações."""

from decimal import Decimal

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.leitura import NivelRiscoEnum
from app.schemas.estacao import CotasSchema, StatusAtualResponse


def classificar_risco(nivel: Decimal, cotas: CotasSchema) -> NivelRiscoEnum:
    """Classifica o nível de risco baseado nas cotas cadastradas.

    Regras:
      - nivel < cota_atencao                 → NORMAL
      - cota_atencao <= nivel < cota_alerta   → ATENCAO
      - cota_alerta <= nivel < cota_emergencia → ALERTA
      - nivel >= cota_emergencia             → EMERGENCIA
    """
    if nivel >= cotas.emergencia:
        return NivelRiscoEnum.EMERGENCIA
    if nivel >= cotas.alerta:
        return NivelRiscoEnum.ALERTA
    if nivel >= cotas.atencao:
        return NivelRiscoEnum.ATENCAO
    return NivelRiscoEnum.NORMAL


async def obter_status_atual_estacoes(db: AsyncSession) -> list[StatusAtualResponse]:
    """Retorna status atual de todas as estações ativas.

    Garante apenas a leitura mais recente por estação ativa.
    Query parametrizada sem concatenação de strings de entrada externa.
    """
    result = await db.execute(
        text("""
            SELECT DISTINCT ON (e.id)
                e.id::text AS estacao_id,
                e.codigo_externo,
                e.nome,
                e.rio,
                l.nivel_metros AS nivel_atual_metros,
                l.classificacao AS classificacao_risco,
                l.data_hora AS data_hora_leitura,
                nr.cota_atencao,
                nr.cota_alerta,
                nr.cota_emergencia,
                (NOW() - l.data_hora > INTERVAL '2 hours') AS dados_desatualizados
            FROM estacoes_monitoramento e
            LEFT JOIN niveis_risco nr ON nr.estacao_id = e.id
            LEFT JOIN leituras_nivel l ON l.estacao_id = e.id
            WHERE e.ativa = TRUE
            ORDER BY e.id, l.data_hora DESC NULLS LAST
        """)
    )
    rows = result.mappings().all()
    status_list: list[StatusAtualResponse] = []
    for row in rows:
        row_dict = dict(row)
        if row_dict.get("nivel_atual_metros") is None or row_dict.get("cota_atencao") is None:
            continue
        cotas_data = {
            "atencao": row_dict.get("cota_atencao"),
            "alerta": row_dict.get("cota_alerta"),
            "emergencia": row_dict.get("cota_emergencia"),
        }
        row_dict["cotas"] = cotas_data
        # A classificação armazenada na leitura representa as cotas vigentes
        # no momento da medição. Como as cotas podem ser alteradas depois,
        # o status atual precisa ser recalculado com os limiares atuais.
        row_dict["classificacao_risco"] = classificar_risco(
            row_dict["nivel_atual_metros"],
            CotasSchema.model_validate(cotas_data),
        ).value
        status_list.append(StatusAtualResponse.model_validate(row_dict))
    return status_list
