"""Aplicação backend e compatibilidade de execução do Agulhas Protege."""

import asyncio
import sys

# O psycopg assíncrono requer um selector loop no Windows. Esta política precisa
# ser definida antes de Alembic, scripts ou Uvicorn criarem o primeiro event loop.
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
