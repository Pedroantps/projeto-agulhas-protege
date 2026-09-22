"""Endpoints operacionais para registro e consulta de ocorrências de campo."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.v1.dependencies import get_db, require_operador
from app.models.ocorrencia import Ocorrencia, StatusOcorrencia
from app.models.usuario import Usuario
from app.schemas.ocorrencia import (
    AtualizarStatusOcorrenciaRequest,
    CriarOcorrenciaRequest,
    OcorrenciaResponse,
)
from app.services.audit_service import registrar_audit_log

router = APIRouter(prefix="/ocorrencias", tags=["Ocorrências"])
limiter = Limiter(key_func=get_remote_address)


@router.get(
    "",
    response_model=list[OcorrenciaResponse],
    summary="Listar ocorrências de campo",
)
async def listar_ocorrencias(
    estacao_id: UUID | None = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
) -> list[OcorrenciaResponse]:
    """Retorna as ocorrências registradas em ordem cronológica decrescente.

    Disponível para acompanhamento das intervenções de campo da Defesa Civil.
    """
    stmt = (
        select(Ocorrencia)
        .options(selectinload(Ocorrencia.estacao), selectinload(Ocorrencia.usuario))
        .order_by(Ocorrencia.criado_em.desc())
        .limit(min(limit, 100))
    )
    if estacao_id:
        stmt = stmt.where(Ocorrencia.estacao_id == estacao_id)

    result = await db.execute(stmt)
    ocorrencias = result.scalars().all()

    return [
        OcorrenciaResponse(
            id=o.id,
            estacao_id=o.estacao_id,
            estacao_nome=o.estacao.nome if o.estacao else None,
            usuario_nome=o.usuario.nome if o.usuario else None,
            alerta_id=o.alerta_id,
            localizacao=o.localizacao,
            descricao=o.descricao,
            status=o.status.value if hasattr(o.status, "value") else str(o.status),
            criado_em=o.criado_em,
            atualizado_em=o.atualizado_em,
        )
        for o in ocorrencias
    ]


@router.post(
    "",
    response_model=OcorrenciaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar ocorrência de campo",
)
@limiter.limit("10/minute")
async def criar_ocorrencia(
    request: Request,
    payload: CriarOcorrenciaRequest,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(require_operador),
) -> OcorrenciaResponse:
    """Requer perfil OPERADOR_DEFESA_CIVIL ou ADMINISTRADOR.

    Registra a intervenção de campo e grava evento no audit_log.
    """
    ocorrencia = Ocorrencia(
        usuario_id=usuario.id,
        estacao_id=payload.estacao_id,
        alerta_id=payload.alerta_id,
        localizacao=payload.localizacao,
        descricao=payload.descricao,
        status=StatusOcorrencia.ABERTA,
    )
    db.add(ocorrencia)
    await db.flush()

    await registrar_audit_log(
        db,
        usuario_id=usuario.id,
        acao="CREATE_OCORRENCIA",
        entidade="ocorrencias",
        entidade_id=ocorrencia.id,
        dados_novos=payload.model_dump(mode="json"),
        ip_address=request.client.host if request.client else None,
        request_id=request.headers.get("X-Request-ID"),
    )

    await db.commit()

    stmt = (
        select(Ocorrencia)
        .options(selectinload(Ocorrencia.estacao), selectinload(Ocorrencia.usuario))
        .where(Ocorrencia.id == ocorrencia.id)
    )
    res = await db.execute(stmt)
    item = res.scalar_one()

    return OcorrenciaResponse(
        id=item.id,
        estacao_id=item.estacao_id,
        estacao_nome=item.estacao.nome if item.estacao else None,
        usuario_nome=item.usuario.nome if item.usuario else usuario.nome,
        alerta_id=item.alerta_id,
        localizacao=item.localizacao,
        descricao=item.descricao,
        status=item.status.value if hasattr(item.status, "value") else str(item.status),
        criado_em=item.criado_em,
        atualizado_em=item.atualizado_em,
    )



@router.patch(
    "/{ocorrencia_id}/status",
    response_model=OcorrenciaResponse,
    summary="Atualizar status da ocorrência",
)
async def atualizar_status_ocorrencia(
    ocorrencia_id: UUID,
    payload: AtualizarStatusOcorrenciaRequest,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(require_operador),
) -> OcorrenciaResponse:
    """Atualiza o status de atendimento da ocorrência (ABERTA, EM_ANDAMENTO, ENCERRADA)."""
    try:
        novo_status = StatusOcorrencia(payload.status)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Status inválido: {payload.status}. Valores permitidos: ABERTA, EM_ANDAMENTO, ENCERRADA.",
        )

    stmt = (
        select(Ocorrencia)
        .options(selectinload(Ocorrencia.estacao), selectinload(Ocorrencia.usuario))
        .where(Ocorrencia.id == ocorrencia_id)
    )
    result = await db.execute(stmt)
    ocorrencia = result.scalar_one_or_none()
    if not ocorrencia:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ocorrência não encontrada.",
        )

    status_anterior = ocorrencia.status
    ocorrencia.status = novo_status
    await db.flush()

    await registrar_audit_log(
        db,
        usuario_id=usuario.id,
        acao="UPDATE_OCORRENCIA_STATUS",
        entidade="ocorrencias",
        entidade_id=ocorrencia.id,
        dados_novos={"status": novo_status.value, "status_anterior": str(status_anterior)},
    )
    await db.commit()

    stmt = (
        select(Ocorrencia)
        .options(selectinload(Ocorrencia.estacao), selectinload(Ocorrencia.usuario))
        .where(Ocorrencia.id == ocorrencia_id)
    )
    res = await db.execute(stmt)
    item = res.scalar_one()

    return OcorrenciaResponse(
        id=item.id,
        estacao_id=item.estacao_id,
        estacao_nome=item.estacao.nome if item.estacao else None,
        usuario_nome=item.usuario.nome if item.usuario else None,
        alerta_id=item.alerta_id,
        localizacao=item.localizacao,
        descricao=item.descricao,
        status=item.status.value if hasattr(item.status, "value") else str(item.status),
        criado_em=item.criado_em,
        atualizado_em=item.atualizado_em,
    )

