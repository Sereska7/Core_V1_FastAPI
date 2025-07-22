"""Create base rabbitmq repository."""

import json
from typing import Any
import aio_pika

from app.internal.repository.v1.rabbitmq.connection import get_connection

__all__ = ["BaseRepository"]


class BaseRepository:
    """Create rabbitmq repository."""

    @staticmethod
    async def create(
        message: Any,
        routing_key: str,
    ):
        """Publishes a message to RabbitMQ.

        Args:
            message (Any): The message to publish.
            routing_key (str): The routing key for the RabbitMQ queue.

        Returns:
            Any: The message that was sent.
        """

        async with get_connection() as channel:
            await channel.default_exchange.publish(
                aio_pika.Message(
                    body=json.dumps(message.to_dict()).encode("utf-8"),
                ),
                routing_key=routing_key,
            )
            return message

    @staticmethod
    async def listen_queue(routing_key: str):
        """Listen to a specific message queue and process incoming messages.

        Args:
            routing_key (str): The routing key (queue name) to listen to.
        """

        async with get_connection() as channel:
            if not isinstance(channel, aio_pika.Channel):
                raise TypeError("Expected aio_pika.Channel, but got something else.")
            queue = await channel.declare_queue(routing_key, durable=True)

            async for message in queue:
                async with message.process():
                    message_body = json.loads(message.body.decode("utf-8"))
                    yield message_body
