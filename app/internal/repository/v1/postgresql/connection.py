"""Create connection to postgresql."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator, Union

from dependency_injector.wiring import Provide, inject
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from app.pkg.connectors import Connectors

__all__ = ["get_connection"]


@asynccontextmanager
@inject
async def get_connection(
    session_factory: async_sessionmaker[AsyncSession] = Provide[
        Connectors.postgresql.session_factory
    ],
    return_engine: bool = False,
    engine: AsyncEngine = Provide[Connectors.postgresql.engine],
) -> AsyncGenerator[Union[AsyncSession, AsyncEngine], None]:
    """Get async SQLAlchemy session or engine.

    Args:
        session_factory:
            async SQLAlchemy session factory.
        return_engine:
            if True, yield SQLAlchemy engine instead of session.
        engine:
            SQLAlchemy AsyncEngine.

    Examples:
        >>> async def exec_query():
        ...     async with get_connection() as session:
        ...         result = await session.execute(text("SELECT * FROM users"))
        ...         users = result.fetchall()

    Yields:
        AsyncSession or AsyncEngine
    """

    if return_engine:
        yield engine
        return

    async with session_factory() as session:
        yield session
