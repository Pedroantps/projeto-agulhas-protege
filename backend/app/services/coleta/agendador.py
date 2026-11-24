"""Agendador em processo: executa a coleta ao subir e a cada intervalo configurado."""

from __future__ import annotations

import asyncio
import contextlib

import structlog

from app.core.config import settings
from app.services.coleta.coletor import executar_coleta

logger = structlog.get_logger()


async def _loop() -> None:
    while True:
        try:
            await executar_coleta()
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("coleta_erro_inesperado")
        await asyncio.sleep(settings.COLETA_INTERVALO_MINUTOS * 60)


def iniciar() -> asyncio.Task[None] | None:
    """Inicia a tarefa de coleta se estiver habilitada."""
    if not settings.COLETA_HABILITADA:
        logger.info("coleta_desabilitada")
        return None
    return asyncio.create_task(_loop(), name="coleta-periodica")


async def parar(tarefa: asyncio.Task[None] | None) -> None:
    """Cancela a tarefa de coleta no desligamento."""
    if tarefa is None:
        return
    tarefa.cancel()
    with contextlib.suppress(asyncio.CancelledError):
        await tarefa
