"""Rabbit connector."""

from contextlib import asynccontextmanager

import aio_pika
import pydantic
from aio_pika.abc import AbstractRobustConnection

from app.pkg.connectors.connector import BaseConnector

__all__ = ["RabbitMQ"]


class RabbitMQ(BaseConnector):
    """RabbitMQ connector."""

    _username: str
    _password: str
    _host: str
    _port: pydantic.PositiveInt

    def __init__(
        self,
        username: str,
        password: pydantic.SecretStr,
        host: str,
        port: pydantic.PositiveInt,
    ):
        self._username = username
        self._password = password.get_secret_value()
        self._host = host
        self._port = port

    def get_dsn(self):
        """Description of ``BaseConnector.get_dsn``."""
        return (
            f"amqp://"
            f"{self._username}:{self._password}@"
            f"{self._host}:{self._port}/"
        )

    async def get_connection(self) -> AbstractRobustConnection:
        """Return connection to RabbitMQ.

        Returns:
            AbstractRobustConnection: Connection to RabbitMQ.
        """
        return await aio_pika.connect_robust(self.get_dsn())

    @asynccontextmanager
    async def get_connect(self) -> aio_pika.Channel:
        """Get connection to RabbitMQ.

        Returns:
            aio_pika.Channel: Connection to RabbitMQ.
        """
        connection = await self.get_connection()

        async with connection:
            channel = await connection.channel()
            yield channel
