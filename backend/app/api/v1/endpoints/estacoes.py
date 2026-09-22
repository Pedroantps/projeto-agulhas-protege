"""Endpoints para estações de monitoramento e gestão de cotas hidrológicas."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import get_db, require_admin
from app.models.niveis_risco import NivelRisco
from app.models.usuario import Usuario
from app.schemas.cotas import AtualizarCotasRequest, CotasResponse
from app.schemas.estacao import StatusAtualResponse
from app.services.audit_service import registrar_audit_log
from app.services.classificacao_risco import obter_status_atual_estacoes

router = APIRouter(prefix="/estacoes", tags=["Estações"])
limiter = Limiter(key_func=get_remote_address)


@router.get(
    "/status-atual",
    response_model=list[StatusAtualResponse],
    summary="Consultar nível atual de todas as estações",
)
@limiter.limit("120/minute")
async def get_status_atual(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> list[StatusAtualResponse]:
    """Endpoint público. Retorna a última leitura de cada estação ativa."""
    return await obter_status_atual_estacoes(db)


@router.put(
    "/{estacao_id}/cotas",
    response_model=CotasResponse,
    summary="Atualizar cotas de risco de uma estação",
)
@limiter.limit("5/minute")
async def atualizar_cotas(
    estacao_id: UUID,
    payload: AtualizarCotasRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: Usuario = Depends(require_admin),
) -> CotasResponse:
    """Requer perfil ADMINISTRADOR.

    Registra dados anteriores e novos na trilha de auditoria.
    """
    result = await db.execute(select(NivelRisco).where(NivelRisco.estacao_id == estacao_id))
    cotas = result.scalar_one_or_none()

    if not cotas:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Estação não encontrada ou sem cotas cadastradas.",
        )

    dados_anteriores = {
        "cota_atencao": str(cotas.cota_atencao),
        "cota_alerta": str(cotas.cota_alerta),
        "cota_emergencia": str(cotas.cota_emergencia),
    }

    cotas.cota_atencao = payload.cota_atencao
    cotas.cota_alerta = payload.cota_alerta
    cotas.cota_emergencia = payload.cota_emergencia
    await db.flush()

    await registrar_audit_log(
        db,
        usuario_id=admin.id,
        acao="UPDATE_COTAS",
        entidade="niveis_risco",
        entidade_id=cotas.id,
        dados_anteriores=dados_anteriores,
        dados_novos=payload.model_dump(mode="json"),
        ip_address=request.client.host if request.client else None,
        request_id=request.headers.get("X-Request-ID"),
    )

    await db.commit()
    await db.refresh(cotas)

    return CotasResponse(
        estacao_id=estacao_id,
        cota_atencao=cotas.cota_atencao,
        cota_alerta=cotas.cota_alerta,
        cota_emergencia=cotas.cota_emergencia,
    )
