"""Folder repository implementation."""

from sqlalchemy import select

from app.internal.repository.repository import Repository
from app.internal.repository.v1.postgresql.connection import get_connection
from app.internal.repository.v1.postgresql.handlers.collect_response import (
    collect_response,
)
from app.pkg.models import v1 as models
from app.pkg.models.sqlalchemy_models import User

__all__ = ["UserRepository"]


class UserRepository(Repository):
    """User repository implementation."""

    @collect_response
    async def read(self) -> list[models.User]:
        async with get_connection() as session:
            stmt = select(User)
            result = await session.execute(stmt)
            users = result.scalars().all()
            return users
