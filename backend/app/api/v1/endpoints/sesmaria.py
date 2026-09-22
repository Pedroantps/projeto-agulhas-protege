"""Endpoints do subsistema de correlação hidrológica e IA do Rio Sesmaria."""

from urllib.parse import quote

from fastapi import APIRouter, Depends, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import get_db
from app.schemas.sesmaria import SesmariaDashboardResponse
from app.services.sesmaria_ia_service import obter_dashboard_sesmaria

router = APIRouter(prefix="/sesmaria", tags=["Rio Sesmaria — IA e Correlação"])
limiter = Limiter(key_func=get_remote_address)


@router.get(
    "/dashboard-ia",
    response_model=SesmariaDashboardResponse,
    summary="Dashboard analítico, preditivo e correlações do Rio Sesmaria",
)
@limiter.limit("120/minute")
async def get_sesmaria_dashboard_ia(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> SesmariaDashboardResponse:
    """Retorna dados de correlação SJB/Resende/Funil, previsão de 1 a 3 dias e recomendação de vazão."""
    return await obter_dashboard_sesmaria(db)


@router.get(
    "/alerta-whatsapp",
    summary="Gera link e mensagem formatada para despacho de alerta via WhatsApp para a Defesa Civil",
)
@limiter.limit("60/minute")
async def get_alerta_whatsapp(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    """Retorna o texto do alerta e URL de redirecionamento pronto para acionamento rápido."""
    dashboard = await obter_dashboard_sesmaria(db)
    texto = dashboard.mensagem_alerta_whatsapp
    url_whatsapp = f"https://wa.me/?text={quote(texto)}"
    return {
        "mensagem": texto,
        "url_whatsapp": url_whatsapp,
    }
