"""Base declarativa e tipos reutilizáveis pelos modelos."""

from datetime import datetime
from typing import Annotated
from uuid import UUID, uuid4

from sqlalchemy import TIMESTAMP, func, text
from sqlalchemy.orm import DeclarativeBase, mapped_column


class Base(DeclarativeBase):
    """Base declarativa dos modelos SQLAlchemy."""


UUIDPrimaryKey = Annotated[
    UUID,
    mapped_column(
        primary_key=True,
        default=uuid4,
        server_default=text("gen_random_uuid()"),
    ),
]

TimestampCreatedAt = Annotated[
    datetime,
    mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False,
    ),
]
