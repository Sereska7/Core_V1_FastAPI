"""Create connection to redis."""

from contextlib import asynccontextmanager
from typing import Union

from dependency_injector.wiring import Provide, inject
from redis.asyncio.connection import Connection, ConnectionPool

from app.pkg.connectors import Connectors

__all__ = ["get_connection"]


@asynccontextmanager
@inject
async def get_connection(
    pool: ConnectionPool = Provide[Connectors.redis.connector],
    return_pool: bool = False,
) -> Union[Connection, ConnectionPool]:
    """Get async connection pool to redis.

    Args:
        pool:
            redis connection pool.
        return_pool:
            if True, return pool, else return connection.

    Returns:
        Async connection to redis.
    """

    if not isinstance(pool, ConnectionPool):
        pool = await pool

    if return_pool:
        yield pool
        return

    async with pool as connection:
        yield connection
