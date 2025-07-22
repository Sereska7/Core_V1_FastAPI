"""Async resource for rabbitmq connector."""

import aio_pika

from app.pkg.connectors.resources import BaseAsyncResource

__all__ = ["RabbitMQ"]


class RabbitMQ(BaseAsyncResource):
    """Rabbitmq connector using aio_pika."""

    async def init(self, dsn: str, *args, **kwargs) -> aio_pika.pool.Pool:
        """Getting connection to RabbitMQ in asynchronous.

        Args:
            dsn: D.S.N - Data Source Name.

        Returns:
            Created connection to RabbitMQ.
        """

        async def get_connect():
            return await aio_pika.connect_robust(dsn)

        return aio_pika.pool.Pool(get_connect, *args, **kwargs)

    async def shutdown(self, resource: aio_pika.pool.Pool):
        """Close connection.

        Args:
            resource: Resource returned by :meth:`.RabbitMQ.init()` method.

        Notes:
            This method is called automatically
            when the application is stopped
            or
            ``Closing`` provider is used.
        """

        await resource.close()
