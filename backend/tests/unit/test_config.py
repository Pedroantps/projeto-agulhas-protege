"""Testes da configuração central."""

import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_rejects_short_jwt_secret() -> None:
    """Uma chave JWT curta deve impedir a inicialização."""
    with pytest.raises(ValidationError):
        Settings(
            DATABASE_URL="postgresql+psycopg://agulhas:test@localhost/agulhas_test",
            JWT_SECRET_KEY="short",
        )
