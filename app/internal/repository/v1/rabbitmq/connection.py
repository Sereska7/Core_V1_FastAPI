"""Create connection to rabbitmq."""

from contextlib import asynccontextmanager
from typing import Union

import aio_pika
from dependency_injector.wiring import Provide, inject

from app.pkg.connectors import Connectors

__all__ = ["get_connection", "acquire_connection"]


@asynccontextmanager
@inject
async def get_connection(
    pool: aio_pika.pool.Pool = Provide[Connectors.rabbitmq.connector],
    return_pool: bool = False,
) -> Union[aio_pika.Channel, aio_pika.pool.Pool]:
    """Get async connection pool to rabbitmq.

    Args:
        pool:
            rabbitmq connection pool.
        return_pool:
            if True, return pool, else return connection.

    Examples:
        If you have a function that contains a query in rabbitmq,
        context manager :func:`.get_connection`
        will get async connection to rabbitmq
        of pool::

            >>> async def exec_some_sql_function() -> None:
            ...     async with get_connection() as c:
            ...         await c.execute("SELECT * FROM users")

    Returns:
        Async connection to rabbitmq.
    """
    if not isinstance(pool, aio_pika.pool.Pool):
        pool = await pool

    if return_pool:
        yield pool
        return

    async with acquire_connection(pool) as channel:
        yield channel


@asynccontextmanager
async def acquire_connection(
    pool: aio_pika.pool.Pool,
) -> aio_pika.Channel:
    """Acquire connection from pool.

    Args:
        pool:
            Getings from :func:`.get_connection` rabbitmq pool.

    Examples:
        If you have a function that contains a query in rabbitmq,
        context manager :func:`.acquire_connection`
        will get async connection to rabbitmq
        of pool::

            >>> async def exec_some_function() -> None:
            ...     async with get_connection(return_pool=True) as __pool:
            ...         async with acquire_connection(__pool) as _cursor:
            ...             queue = await _cursor.get_queue("queue_name")
            ...             await queue.get()
            ...         async with acquire_connection(__pool) as _cursor:
            ...             queue = await _cursor.get_queue("queue_name")
            ...             await queue.get()

    Returns:
        Async connection to rabbitmq.
    """
    async with pool.acquire() as conn:
        channel = await conn.channel()
        yield channel
