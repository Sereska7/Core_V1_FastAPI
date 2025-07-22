"""Async resource for Redis connector."""

from redis.asyncio import ConnectionPool, from_url

from app.pkg.connectors.resources import BaseAsyncResource

__all__ = ["RedisResource"]


class RedisResource(BaseAsyncResource):
    """Redis connector using aiopg."""

    async def init(self, dsn: str, *args, **kwargs) -> ConnectionPool:
        """Getting connection pool in asynchronous.

        Args:
            dsn: D.S.N - Data Source Name.

        Returns:
            Created connection pool.
        """

        return await from_url(url=dsn, **kwargs)

    async def shutdown(self, resource: ConnectionPool) -> None:
        """Close connection.

        Args:
            resource: Resource returned by :meth:`.Redis.init()` method.

        Notes:
            This method is called automatically
            when the application is stopped
            or
            ``Closing`` provider is used.
        """

        await resource.disconnect()
