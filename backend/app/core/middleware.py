"""Middlewares HTTP compartilhados pela aplicação."""

from collections.abc import Awaitable, Callable
from uuid import uuid4

import structlog
from fastapi import Request, Response

logger = structlog.get_logger()

RequestHandler = Callable[[Request], Awaitable[Response]]


async def logging_middleware(request: Request, call_next: RequestHandler) -> Response:
    """Registra a requisição com um identificador de correlação."""
    request_id = request.headers.get("X-Request-ID", str(uuid4()))
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(request_id=request_id)
    logger.info("request_started", method=request.method, path=request.url.path)
    response = await call_next(request)
    logger.info("request_completed", status_code=response.status_code)
    response.headers["X-Request-ID"] = request_id
    return response


async def security_headers_middleware(request: Request, call_next: RequestHandler) -> Response:
    """Inclui cabeçalhos defensivos em todas as respostas."""
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "0"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self'; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "img-src 'self' data: https://resources.cemaden.gov.br; "
        "connect-src 'self'"
    )
    return response
