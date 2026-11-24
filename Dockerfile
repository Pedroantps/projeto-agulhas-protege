# Imagem única de produção: API FastAPI + frontend React compilado servido pelo mesmo domínio.
FROM node:20-alpine AS frontend
WORKDIR /web
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend ./
RUN npm run build

FROM python:3.12-slim-bookworm
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    FRONTEND_DIST_DIR=/app/static \
    PATH="/app/.venv/bin:$PATH"
WORKDIR /app
RUN pip install --no-cache-dir uv

COPY backend/pyproject.toml backend/uv.lock ./
RUN uv sync --frozen --no-dev

COPY backend/app ./app
COPY backend/scripts ./scripts
COPY backend/alembic.ini ./
COPY --from=frontend /web/dist ./static

EXPOSE 8000
# Migra o banco, garante usuários/estação (idempotente) e sobe a API.
# --proxy-headers: o rate limit por IP precisa enxergar o IP real atrás do proxy do provedor.
CMD ["sh", "-c", "alembic upgrade head && python scripts/seed.py --sem-coleta && exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --proxy-headers --forwarded-allow-ips='*'"]
